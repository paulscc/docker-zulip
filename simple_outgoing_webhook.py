#!/usr/bin/env python3
"""
Simple Outgoing Webhook for Zulip
Detects messages and sends data to Kafka with better logging
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any
from kafka import KafkaProducer

# Configure logging with better format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleOutgoingWebhook:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the outgoing webhook with configuration"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_unread = "zulip-unread-messages"
        
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
    
    def get_recent_messages(self, stream: str, topic: str, limit: int = 10) -> List[Dict]:
        """Get recent messages from a stream/topic"""
        try:
            url = f"{self.outgoing_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.outgoing_bot['api_key']}",
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
                
                # Add direct links to each message
                for message in messages:
                    message_id = message.get("id")
                    if message_id:
                        # Construct direct link to the message
                        server_url = self.outgoing_bot['server_url'].replace('https://', '').replace('http://', '')
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
                return []
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def send_to_kafka(self, data: Dict) -> bool:
        """Send messages data to Kafka topic"""
        try:
            if not self.producer:
                logger.error("Kafka producer not initialized")
                return False
            
            # Process messages to include essential info with links
            processed_messages = []
            for msg in data.get("messages", []):
                processed_msg = {
                    "id": msg.get("id"),
                    "content": msg.get("content", ""),
                    "sender_full_name": msg.get("sender_full_name", "Unknown"),
                    "timestamp": msg.get("timestamp", 0),
                    "direct_link": msg.get("direct_link", "")
                }
                processed_messages.append(processed_msg)
            
            payload = {
                "message_type": "unread_messages",
                "timestamp": datetime.now().isoformat(),
                "stream": data.get("stream"),
                "topic": data.get("topic"),
                "messages": processed_messages,
                "message_count": len(processed_messages),
                "processed_at": datetime.now().isoformat(),
                "webhook_token": self.outgoing_bot.get("webhook_token")
            }
            
            # Send to Kafka
            try:
                key = f"{data.get('stream')}-{data.get('topic')}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                
                future = self.producer.send(
                    self.kafka_topic_unread,
                    key=key,
                    value=payload
                )
                
                # Wait for the message to be sent
                record_metadata = future.get(timeout=30)
                
                logger.info(f"Messages sent successfully to Kafka!")
                logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                return True
                
            except Exception as e:
                logger.error(f"Error sending to Kafka: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return False
    
    def monitor_streams(self):
        """Monitor configured streams and send messages to Kafka"""
        logger.info("Starting simple stream monitoring...")
        
        # Get streams to monitor from bot configuration
        streams_to_monitor = {}
        for channel in self.outgoing_bot.get("channels", []):
            stream = channel.get("stream")
            topic = channel.get("topic")
            if stream and topic:
                streams_to_monitor[f"{stream}/{topic}"] = {"stream": stream, "topic": topic}
        
        logger.info(f"Monitoring {len(streams_to_monitor)} stream/topic combinations")
        
        while True:
            try:
                current_time = datetime.now()
                logger.info(f"=== Checking streams at {current_time.strftime('%H:%M:%S')} ===")
                
                for key, stream_data in streams_to_monitor.items():
                    stream = stream_data["stream"]
                    topic = stream_data["topic"]
                    
                    logger.info(f"Checking {stream}/{topic}")
                    
                    # Get recent messages (always send latest messages)
                    messages = self.get_recent_messages(stream, topic, limit=5)
                    
                    if messages:
                        logger.info(f"Found {len(messages)} messages in {stream}/{topic}")
                        
                        # Send to Kafka
                        data = {
                            "stream": stream,
                            "topic": topic,
                            "messages": messages,
                            "message_count": len(messages)
                        }
                        
                        success = self.send_to_kafka(data)
                        
                        if success:
                            logger.info(f"Successfully sent messages for {stream}/{topic}")
                        else:
                            logger.error(f"Failed to send messages for {stream}/{topic}")
                    else:
                        logger.info(f"No messages found for {stream}/{topic}")
                
                # Wait before next check
                logger.info("Waiting 30 seconds before next check...")
                time.sleep(30)  # Check every 30 seconds instead of 60
                
            except KeyboardInterrupt:
                logger.info("Stopping monitoring...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying

def main():
    """Main function to run the simple outgoing webhook"""
    webhook = SimpleOutgoingWebhook()
    
    try:
        logger.info("Starting Simple Outgoing Webhook...")
        webhook.monitor_streams()
    except KeyboardInterrupt:
        logger.info("Simple Outgoing Webhook stopped by user")
    except Exception as e:
        logger.error(f"Simple Outgoing Webhook error: {e}")

if __name__ == "__main__":
    main()
