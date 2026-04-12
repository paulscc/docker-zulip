#!/usr/bin/env python3
"""
Incoming Webhook for Zulip
Consumes summaries from Kafka and publishes to Zulip streams/topics
"""

import requests
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IncomingWebhook:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the incoming webhook with configuration"""
        self.config = self.load_config(config_file)
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_summaries = "zulip-summaries"
        
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
    
    def publish_summary(self, stream: str, topic: str, summary: str, original_topic: str = None) -> bool:
        """Publish summary to Zulip stream/topic"""
        try:
            url = f"{self.incoming_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Create message content
            if original_topic:
                message_content = f"""**Resumen Automático** - {stream}/{original_topic}

{summary}

---
*Generado por IA usando Ollama - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                target_topic = f"resumen-{original_topic}"
            else:
                message_content = f"""**Resumen Automático**

{summary}

---
*Generado por IA usando Ollama - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
                target_topic = topic
            
            payload = {
                "type": "stream",
                "to": stream,
                "topic": target_topic,
                "content": message_content
            }
            
            response = requests.post(url, headers=headers, json=payload, verify=False)
            
            if response.status_code == 200:
                logger.info(f"Summary published successfully to {stream}/{target_topic}")
                return True
            else:
                logger.error(f"Error publishing summary: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing summary: {e}")
            return False
    
    def create_summary_topic(self, stream: str, original_topic: str) -> bool:
        """Create a summary topic if it doesn't exist"""
        try:
            # First, publish a marker message to create the topic
            marker_content = f"""**Tema de Resúmenes** - {original_topic}

Este tema contendrá los resúmenes automáticos generados para el topic "{original_topic}".

Los resúmenes se generarán cuando se detecten suficientes mensajes no leídos en el topic original.

---
*Configurado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            return self.publish_summary(stream, f"resumen-{original_topic}", marker_content)
            
        except Exception as e:
            logger.error(f"Error creating summary topic: {e}")
            return False
    
    def consume_summaries_from_kafka(self):
        """Consume summaries from Kafka and publish to Zulip"""
        logger.info(f"Starting Kafka consumer for summaries topic '{self.kafka_topic_summaries}'...")
        
        while True:
            try:
                # Use kafka-console-consumer to read messages
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", self.kafka_topic_summaries,
                    "--from-beginning",
                    "--max-messages", "1",
                    "--timeout-ms", "5000"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parse the JSON message
                    try:
                        summary_data = json.loads(result.stdout.strip())
                        logger.info(f"Received summary from Kafka: {summary_data.get('original_stream')}/{summary_data.get('original_topic')}")
                        
                        # Verify message type
                        if summary_data.get("message_type") != "summary":
                            logger.warning("Not a summary message, skipping")
                            continue
                        
                        # Verify webhook token if present
                        expected_token = self.incoming_bot.get("webhook_token")
                        if expected_token and summary_data.get("webhook_token") != expected_token:
                            logger.warning("Invalid webhook token, skipping message")
                            continue
                        
                        # Extract summary data
                        stream = summary_data.get("original_stream")
                        topic = summary_data.get("original_topic")
                        summary = summary_data.get("summary")
                        
                        if not stream or not topic or not summary:
                            logger.warning("Invalid summary format, skipping")
                            continue
                        
                        # Publish summary to Zulip
                        logger.info(f"Publishing summary to Zulip: {stream}/resumen-{topic}")
                        success = self.publish_summary(stream, f"resumen-{topic}", summary, topic)
                        
                        if success:
                            logger.info(f"Successfully published summary for {stream}/{topic}")
                        else:
                            logger.error(f"Failed to publish summary for {stream}/{topic}")
                            
                    except json.JSONDecodeError as e:
                        logger.error(f"Error parsing JSON summary: {e}")
                    except Exception as e:
                        logger.error(f"Error processing summary: {e}")
                else:
                    # No messages received, wait a bit
                    time.sleep(5)
                
            except subprocess.TimeoutExpired:
                # Timeout is expected when no messages are available
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Stopping Kafka summary consumer...")
                break
            except Exception as e:
                logger.error(f"Error in consumer loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def send_test_message(self, stream: str, topic: str) -> bool:
        """Send a test message to verify webhook is working"""
        try:
            test_content = f"""**Mensaje de Prueba** - Incoming Webhook

Este es un mensaje de prueba para verificar que el incoming webhook está funcionando correctamente.

Stream: {stream}
Topic: {topic}
Bot: {self.incoming_bot.get('bot_name')}
Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Si ves este mensaje, el webhook está configurado correctamente.
"""
            
            return self.publish_summary(stream, topic, test_content)
            
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return False

def main():
    """Main function to run the incoming webhook consumer"""
    webhook = IncomingWebhook()
    
    try:
        logger.info("Starting Kafka Summary Consumer for Zulip...")
        webhook.consume_summaries_from_kafka()
    except KeyboardInterrupt:
        logger.info("Kafka Summary Consumer stopped by user")
    except Exception as e:
        logger.error(f"Kafka Summary Consumer error: {e}")

if __name__ == "__main__":
    main()
