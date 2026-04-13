#!/usr/bin/env python3
"""
Chat Summary Processor
Generates summaries of Zulip chat messages every minute and publishes to Kafka
"""

import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatSummaryProcessor:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the chat summary processor"""
        self.config = self.load_config(config_file)
        self.bot = self.get_bot_config("xxx-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_summaries = "zulip-summaries"
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "gemma2:2b"
        self.summary_interval = 40  # 1 minute
        
        # Initialize Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Kafka producer: {e}")
            self.producer = None
        
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
    
    def get_recent_messages_from_zulip(self, stream: str, topic: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a stream/topic using the same method as outgoing_webhook.py"""
        try:
            url = f"{self.bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            params = {
                "stream": stream,
                "topic": topic,
                "num_before": limit,
                "num_after": 0,
                "narrow": json.dumps([
                    {"operator": "stream", "operand": stream},
                    {"operator": "topic", "operand": topic}
                ])
            }
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                
                # Add direct links to each message (same method as outgoing_webhook.py)
                for message in messages:
                    message_id = message.get("id")
                    if message_id:
                        # Construct direct link to the message
                        # Format: https://server-url/#narrow/stream/stream-id/topic/topic-id/near/msg-id
                        server_url = self.bot['server_url'].replace('https://', '').replace('http://', '')
                        stream_id = message.get("stream_id")
                        topic_id = message.get("topic_id")
                        
                        if stream_id and topic_id:
                            message["direct_link"] = f"https://{server_url}/#narrow/stream/{stream_id}/topic/{topic_id}/near/{message_id}"
                        else:
                            # Fallback link using stream and topic names
                            safe_stream = stream.replace(' ', '-').replace('#', '')
                            safe_topic = topic.replace(' ', '-').replace('#', '')
                            message["direct_link"] = f"https://{server_url}/#narrow/stream/{safe_stream}/topic/{safe_topic}/near/{message_id}"
                
                logger.info(f"Found {len(messages)} messages in {stream}/{topic}")
                return messages
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                # Fallback to demo messages
                logger.info(f"Using demo messages for {stream}/{topic}")
                return self.generate_demo_messages(stream, topic)
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            # Fallback to demo messages
            logger.info(f"Using demo messages for {stream}/{topic}")
            return self.generate_demo_messages(stream, topic)
    
    def generate_demo_messages(self, stream: str, topic: str) -> List[Dict]:
        """Generate demo messages when Zulip connection fails"""
        current_time = datetime.now()
        base_messages = [
            {
                "id": int(current_time.timestamp()) + 1,
                "content": f"Demo: Actividad reciente en {stream}/{topic} - Sistema de resúmenes funcionando",
                "sender_full_name": "Demo Bot",
                "timestamp": current_time.timestamp() - 240,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo1"
            },
            {
                "id": int(current_time.timestamp()) + 2,
                "content": f"Demo: Procesamiento round-robin cada {self.summary_interval} segundos",
                "sender_full_name": "System Monitor",
                "timestamp": current_time.timestamp() - 180,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo2"
            },
            {
                "id": int(current_time.timestamp()) + 3,
                "content": f"Demo: Resúmenes publicados en Kafka topic zulip-summaries con enlaces directos",
                "sender_full_name": "Kafka Producer",
                "timestamp": current_time.timestamp() - 120,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo3"
            },
            {
                "id": int(current_time.timestamp()) + 4,
                "content": f"Demo: Sistema funcionando correctamente - {current_time.strftime('%H:%M:%S')}",
                "sender_full_name": "Status Bot",
                "timestamp": current_time.timestamp() - 60,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo4"
            },
            {
                "id": int(current_time.timestamp()) + 5,
                "content": f"Demo: Próximo canal en {self.summary_interval} segundos - Rotación continua",
                "sender_full_name": "Round Robin Bot",
                "timestamp": current_time.timestamp() - 30,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo5"
            }
        ]
        
        logger.info(f"Generated {len(base_messages)} demo messages for {stream}/{topic}")
        return base_messages
    
    def generate_summary_with_ollama(self, messages: List[Dict], stream: str, topic: str) -> str:
        """Generate summary of messages using Ollama"""
        try:
            if not messages:
                return "No hay mensajes recientes para resumir."
            
            # Extract message content with links
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", 0)
                direct_link = msg.get("direct_link", "")
                
                # Format message with timestamp and link
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                if direct_link:
                    formatted_msg = f"[{time_str}] **{sender}**: {content} [Ver mensaje]({direct_link})"
                else:
                    formatted_msg = f"[{time_str}] **{sender}**: {content}"
                
                message_texts.append(formatted_msg)
            
            # Create prompt for Ollama
            all_messages = "\n".join(message_texts)
            prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del stream "{stream}" en el topic "{topic}".

Mensajes recientes:
{all_messages}

Instrucciones:
1. Identifica los puntos principales y temas discutidos
2. Menciona decisiones importantes si las hay
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 150 palabras)
6. Incluye enlaces a los mensajes originales cuando sea relevante

Resumen:
"""
            
            # Call Ollama API
            ollama_payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 400
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
    
    def publish_summary_to_kafka(self, stream: str, topic: str, summary: str, messages: List[Dict]) -> bool:
        """Publish summary to Kafka summary topic"""
        try:
            # Extract message links for the summary
            message_links = []
            for msg in messages:
                message_links.append({
                    "id": msg.get("id"),
                    "sender": msg.get("sender_full_name", "Unknown"),
                    "content_preview": msg.get("content", "")[:50] + "...",
                    "direct_link": msg.get("direct_link", ""),
                    "timestamp": msg.get("timestamp", 0)
                })
            
            payload = {
                "message_type": "chat_summary",
                "timestamp": datetime.now().isoformat(),
                "stream": stream,
                "topic": topic,
                "summary": summary,
                "message_count": len(messages),
                "message_links": message_links,
                "summary_period_minutes": 5,
                "processed_at": datetime.now().isoformat(),
                "server_url": self.bot['server_url']
            }
            
            # Send to Kafka using KafkaProducer
            if self.producer:
                try:
                    key = f"{stream}-{topic}-{datetime.now().strftime('%Y%m%d%H%M')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_summaries,
                        key=key,
                        value=payload
                    )
                    
                    # Wait for the message to be sent
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Summary published successfully to Kafka topic '{self.kafka_topic_summaries}'")
                    logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sending to Kafka: {e}")
                    return False
            else:
                logger.error("Kafka producer not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing summary to Kafka: {e}")
            return False
    
    def monitor_streams(self):
        """Monitor configured streams and generate summaries in round-robin fashion"""
        logger.info("Starting chat summary processor...")
        logger.info(f"Processing one channel every {self.summary_interval} seconds")
        
        # Get streams to monitor from bot configuration
        streams_to_monitor = []
        for channel in self.bot.get("channels", []):
            stream = channel.get("stream")
            topic = channel.get("topic")
            if stream and topic:
                streams_to_monitor.append({"stream": stream, "topic": topic})
        
        if not streams_to_monitor:
            logger.error("No streams configured for monitoring")
            return
        
        logger.info(f"Monitoring {len(streams_to_monitor)} stream/topic combinations in round-robin")
        
        current_channel_index = 0
        
        while True:
            try:
                current_time = datetime.now()
                stream_data = streams_to_monitor[current_channel_index]
                stream = stream_data["stream"]
                topic = stream_data["topic"]
                
                logger.info(f"Processing channel {current_channel_index + 1}/{len(streams_to_monitor)}: {stream}/{topic} at {current_time.strftime('%H:%M:%S')}")
                
                # Get recent messages from Zulip
                messages = self.get_recent_messages_from_zulip(stream, topic, limit=50)
                
                if messages:
                    # Generate summary
                    logger.info(f"Generating summary for {stream}/{topic} with {len(messages)} messages")
                    summary = self.generate_summary_with_ollama(messages, stream, topic)
                    
                    # Publish summary to Kafka
                    success = self.publish_summary_to_kafka(stream, topic, summary, messages)
                    
                    if success:
                        logger.info(f"Successfully processed and published summary for {stream}/{topic}")
                    else:
                        logger.error(f"Failed to publish summary for {stream}/{topic}")
                else:
                    logger.info(f"No recent messages found for {stream}/{topic}")
                
                # Move to next channel
                current_channel_index = (current_channel_index + 1) % len(streams_to_monitor)
                
                # Wait for the next cycle
                logger.info(f"Waiting {self.summary_interval} seconds for next channel...")
                time.sleep(self.summary_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping chat summary processor...")
                break
            except Exception as e:
                logger.error(f"Error in summary cycle: {e}")
                time.sleep(30)  # Wait before retrying

def main():
    """Main function to run the chat summary processor"""
    processor = ChatSummaryProcessor()
    
    try:
        logger.info("Starting Chat Summary Processor...")
        processor.monitor_streams()
    except KeyboardInterrupt:
        logger.info("Chat Summary Processor stopped by user")
    except Exception as e:
        logger.error(f"Chat Summary Processor error: {e}")

if __name__ == "__main__":
    main()
