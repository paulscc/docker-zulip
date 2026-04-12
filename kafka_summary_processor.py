#!/usr/bin/env python3
"""
Kafka Summary Consumer
Consumes unread messages from Kafka, generates summaries with Ollama, and publishes to summary topic
"""

import json
import logging
import subprocess
import requests
from datetime import datetime
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaSummaryProcessor:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the Kafka summary processor"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_unread = "zulip-unread-messages"
        self.kafka_topic_summaries = "zulip-summaries"
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "gemma2:2b"
        
    def load_config(self, config_file: str) -> Dict:
        """Load bot configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get_bot_config(self, bot_name: str) -> Dict:
        """Get specific bot configuration"""
        for bot in self.config.get("bots", []):
            if bot.get("bot_name") == bot_name:
                return bot
        return {}
    
    def generate_summary_with_ollama(self, messages: List[Dict], stream: str, topic: str) -> str:
        """Generate summary of messages using Ollama"""
        try:
            # Extract message content
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", "")
                
                # Format message for summary
                formatted_msg = f"[{sender}]: {content}"
                message_texts.append(formatted_msg)
            
            # Create prompt for Ollama
            all_messages = "\n".join(message_texts)
            prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del stream "{stream}" en el topic "{topic}".

Mensajes:
{all_messages}

Instrucciones:
1. Identifica los puntos principales y temas discutidos
2. Menciona decisiones importantes si las hay
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 200 palabras)

Resumen:
"""
            
            # Call Ollama API
            ollama_payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "").strip()
                logger.info(f"Generated summary for {stream}/{topic}")
                return summary
            else:
                logger.error(f"Error calling Ollama: {response.status_code}")
                return f"Error generando resumen para {stream}/{topic}"
                
        except Exception as e:
            logger.error(f"Error generating summary with Ollama: {e}")
            return f"No se pudo generar el resumen debido a un error: {str(e)}"
    
    def publish_summary_to_kafka(self, stream: str, topic: str, summary: str, original_data: Dict) -> bool:
        """Publish summary to Kafka summary topic"""
        try:
            payload = {
                "message_type": "summary",
                "timestamp": datetime.now().isoformat(),
                "original_stream": stream,
                "original_topic": topic,
                "summary": summary,
                "original_message_count": original_data.get("message_count", 0),
                "processed_at": datetime.now().isoformat(),
                "webhook_token": self.outgoing_bot.get("webhook_token")
            }
            
            # Convert to JSON string for Kafka
            message_json = json.dumps(payload)
            
            # Send to Kafka using docker exec
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {self.kafka_topic_summaries}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Summary published successfully to Kafka topic '{self.kafka_topic_summaries}'")
                return True
            else:
                logger.error(f"Error publishing summary to Kafka: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing summary to Kafka: {e}")
            return False
    
    def consume_messages(self):
        """Consume messages from Kafka unread topic and process them"""
        logger.info(f"Starting Kafka consumer for topic '{self.kafka_topic_unread}'...")
        
        while True:
            try:
                # Use kafka-console-consumer to read messages
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", self.kafka_topic_unread,
                    "--from-beginning",
                    "--max-messages", "1",
                    "--timeout-ms", "5000"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse the JSON message
                    try:
                        message_data = json.loads(result.stdout.strip())
                        logger.info(f"Received message from Kafka: {message_data.get('stream')}/{message_data.get('topic')}")
                        
                        # Verify webhook token if present
                        expected_token = self.outgoing_bot.get("webhook_token")
                        if expected_token and message_data.get("webhook_token") != expected_token:
                            logger.warning("Invalid webhook token, skipping message")
                            continue
                        
                        # Extract message data
                        stream = message_data.get("stream")
                        topic = message_data.get("topic")
                        messages = message_data.get("messages", [])
                        
                        if not stream or not topic or not messages:
                            logger.warning("Invalid message format, skipping")
                            continue
                        
                        # Generate summary
                        logger.info(f"Generating summary for {stream}/{topic} with {len(messages)} messages")
                        summary = self.generate_summary_with_ollama(messages, stream, topic)
                        
                        # Publish summary to Kafka
                        success = self.publish_summary_to_kafka(stream, topic, summary, message_data)
                        
                        if success:
                            logger.info(f"Successfully processed and published summary for {stream}/{topic}")
                        else:
                            logger.error(f"Failed to publish summary for {stream}/{topic}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON message: {e}")
                    except Exception as e:
                        logger.error(f"Error processing message: {e}")
                else:
                    # No messages received, wait a bit
                    time.sleep(5)
                
            except subprocess.TimeoutExpired:
                # Timeout is expected when no messages are available
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Stopping Kafka consumer...")
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                time.sleep(10)  # Wait before retrying

def main():
    """Main function to run the Kafka summary processor"""
    processor = KafkaSummaryProcessor()
    
    try:
        logger.info("Starting Kafka Summary Processor...")
        processor.consume_messages()
    except KeyboardInterrupt:
        logger.info("Kafka Summary Processor stopped by user")
    except Exception as e:
        logger.error(f"Kafka Summary Processor error: {e}")

if __name__ == "__main__":
    main()
