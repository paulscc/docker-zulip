#!/usr/bin/env python3
"""
Outgoing Webhook for Zulip
Detects triggers (unread messages) and sends data to Kafka
"""

import requests
import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Any

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
            
            response = requests.get(url, headers=headers, params=params, verify=False)
            if response.status_code == 200:
                return response.json().get("messages", [])
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def send_to_kafka(self, data: Dict) -> bool:
        """Send unread messages data to Kafka topic"""
        try:
            payload = {
                "trigger_type": "unread_messages",
                "timestamp": datetime.now().isoformat(),
                "stream": data.get("stream"),
                "topic": data.get("topic"),
                "messages": data.get("messages", []),
                "message_count": data.get("message_count", 0),
                "webhook_token": self.outgoing_bot.get("webhook_token")
            }
            
            # Convert to JSON string for Kafka
            message_json = json.dumps(payload)
            
            # Send to Kafka using docker exec
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {self.kafka_topic_unread}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Data sent successfully to Kafka topic '{self.kafka_topic_unread}'")
                return True
            else:
                logger.error(f"Error sending to Kafka: {result.stderr}")
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
