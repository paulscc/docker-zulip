#!/usr/bin/env python3
"""
Outgoing Webhook for Zulip
Detects triggers (unread messages) and sends data to Kafka
"""

import requests
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutgoingWebhook:
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
    
    def check_unread_messages(self, stream: str, topic: str, threshold: int = 10) -> bool:
        """Check if there are unread messages above threshold"""
        try:
            # Get messages from the stream/topic
            url = f"{self.outgoing_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.outgoing_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            params = {
                "stream": stream,
                "topic": topic,
                "narrow": json.dumps([
                    {"operator": "stream", "operand": stream},
                    {"operator": "topic", "operand": topic}
                ])
            }
            
            response = requests.get(url, headers=headers, params=params, verify=False)
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                unread_count = len([msg for msg in messages if not msg.get("flags", {}).get("read", False)])
                
                logger.info(f"Found {unread_count} unread messages in {stream}/{topic}")
                return unread_count >= threshold
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error checking unread messages: {e}")
            return False
    
    def get_recent_messages(self, stream: str, topic: str, limit: int = 50) -> List[Dict]:
        """Get recent messages from a stream/topic with links"""
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
            
            response = requests.get(url, headers=headers, params=params, verify=False)
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                
                # Add direct links to each message
                for message in messages:
                    message_id = message.get("id")
                    if message_id:
                        # Construct direct link to the message
                        # Format: https://server-url/#narrow/stream/stream-id/topic/topic-id/near/msg-id
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
                
                return messages
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def send_to_kafka(self, data: Dict) -> bool:
        """Send unread messages data to Kafka topic with links"""
        try:
            # Process messages to include essential info with links
            processed_messages = []
            for msg in data.get("messages", []):
                processed_msg = {
                    "id": msg.get("id"),
                    "content": msg.get("content", ""),
                    "sender_full_name": msg.get("sender_full_name", ""),
                    "timestamp": msg.get("timestamp", ""),
                    "direct_link": msg.get("direct_link", ""),
                    "reactions": msg.get("reactions", []),
                    "flags": msg.get("flags", {})
                }
                processed_messages.append(processed_msg)
            
            payload = {
                "trigger_type": "unread_messages",
                "timestamp": datetime.now().isoformat(),
                "stream": data.get("stream"),
                "topic": data.get("topic"),
                "messages": processed_messages,
                "message_count": data.get("message_count", 0),
                "webhook_token": self.outgoing_bot.get("webhook_token"),
                "server_url": self.outgoing_bot['server_url']
            }
            
            # Send to Kafka using KafkaProducer
            if self.producer:
                try:
                    # Send message with key as stream/topic combination
                    key = f"{data.get('stream')}-{data.get('topic')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_unread,
                        key=key,
                        value=payload
                    )
                    
                    # Wait for the message to be sent
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Data sent successfully to Kafka topic '{self.kafka_topic_unread}'")
                    logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sending to Kafka: {e}")
                    return False
            else:
                logger.error("Kafka producer not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return False
    
    def monitor_streams(self):
        """Monitor configured streams for triggers"""
        logger.info("Starting stream monitoring...")
        
        # Get streams to monitor from bot configuration
        streams_to_monitor = {}
        for channel in self.outgoing_bot.get("channels", []):
            stream = channel.get("stream")
            topic = channel.get("topic")
            if stream and topic:
                streams_to_monitor[f"{stream}/{topic}"] = {"stream": stream, "topic": topic}
        
        while True:
            try:
                for key, stream_data in streams_to_monitor.items():
                    stream = stream_data["stream"]
                    topic = stream_data["topic"]
                    
                    # Check for unread messages
                    if self.check_unread_messages(stream, topic):
                        logger.info(f"Trigger detected in {stream}/{topic}")
                        
                        # Get recent messages
                        messages = self.get_recent_messages(stream, topic)
                        
                        # Send to Kafka
                        data = {
                            "stream": stream,
                            "topic": topic,
                            "messages": messages,
                            "message_count": len(messages)
                        }
                        
                        self.send_to_kafka(data)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Stopping monitoring...")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying

def main():
    """Main function to run the outgoing webhook"""
    webhook = OutgoingWebhook()
    
    try:
        webhook.monitor_streams()
    except KeyboardInterrupt:
        logger.info("Outgoing webhook stopped by user")
    except Exception as e:
        logger.error(f"Outgoing webhook error: {e}")

if __name__ == "__main__":
    main()
