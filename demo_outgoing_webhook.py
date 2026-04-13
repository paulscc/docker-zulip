#!/usr/bin/env python3
"""
Demo Outgoing Webhook for Zulip
Generates demo messages and sends them to Kafka for testing
"""

import json
import logging
import time
from datetime import datetime
from typing import Dict, List
from kafka import KafkaProducer

# Configure logging with better format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DemoOutgoingWebhook:
    def __init__(self):
        """Initialize the demo outgoing webhook"""
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
    
    def generate_demo_messages(self, stream: str, topic: str) -> List[Dict]:
        """Generate demo messages for testing"""
        current_time = datetime.now()
        
        demo_messages = [
            {
                "id": int(current_time.timestamp()) + 1,
                "content": f"Demo message 1 in {stream}/{topic} - Sistema de webhook funcionando",
                "sender_full_name": "Demo User 1",
                "timestamp": current_time.timestamp() - 240,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo1"
            },
            {
                "id": int(current_time.timestamp()) + 2,
                "content": f"Demo message 2 in {stream}/{topic} - Enlaces directos incluidos",
                "sender_full_name": "Demo User 2",
                "timestamp": current_time.timestamp() - 180,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo2"
            },
            {
                "id": int(current_time.timestamp()) + 3,
                "content": f"Demo message 3 in {stream}/{topic} - Publicación en Kafka exitosa",
                "sender_full_name": "Demo User 3",
                "timestamp": current_time.timestamp() - 120,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/demo3"
            }
        ]
        
        logger.info(f"Generated {len(demo_messages)} demo messages for {stream}/{topic}")
        return demo_messages
    
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
                "message_type": "demo_unread_messages",
                "timestamp": datetime.now().isoformat(),
                "stream": data.get("stream"),
                "topic": data.get("topic"),
                "messages": processed_messages,
                "message_count": len(processed_messages),
                "processed_at": datetime.now().isoformat(),
                "webhook_token": "demo_token",
                "demo_mode": True
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
                
                logger.info(f"Demo messages sent successfully to Kafka!")
                logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                return True
                
            except Exception as e:
                logger.error(f"Error sending to Kafka: {e}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return False
    
    def run_demo(self):
        """Run demo webhook with messages to Kafka"""
        logger.info("Starting Demo Outgoing Webhook...")
        
        # Demo streams to process
        demo_streams = [
            {"stream": "comercio", "topic": "general"},
            {"stream": "desarrollo", "topic": "general"},
            {"stream": "equipo", "topic": "general"},
            {"stream": "general", "topic": "chat"}
        ]
        
        logger.info(f"Processing {len(demo_streams)} stream/topic combinations")
        
        cycle_count = 0
        max_cycles = 6  # 6 ciclos para prueba
        
        while cycle_count < max_cycles:
            try:
                current_time = datetime.now()
                logger.info(f"=== Demo Cycle {cycle_count + 1}/{max_cycles} at {current_time.strftime('%H:%M:%S')} ===")
                
                for stream_data in demo_streams:
                    stream = stream_data["stream"]
                    topic = stream_data["topic"]
                    
                    logger.info(f"Processing {stream}/{topic}")
                    
                    # Generate demo messages
                    messages = self.generate_demo_messages(stream, topic)
                    
                    if messages:
                        logger.info(f"Generated {len(messages)} demo messages for {stream}/{topic}")
                        
                        # Send to Kafka
                        data = {
                            "stream": stream,
                            "topic": topic,
                            "messages": messages,
                            "message_count": len(messages)
                        }
                        
                        success = self.send_to_kafka(data)
                        
                        if success:
                            logger.info(f"Successfully sent demo messages for {stream}/{topic}")
                        else:
                            logger.error(f"Failed to send demo messages for {stream}/{topic}")
                    
                    # Small delay between streams
                    time.sleep(2)
                
                cycle_count += 1
                
                if cycle_count < max_cycles:
                    # Wait before next cycle
                    logger.info("Waiting 15 seconds before next demo cycle...")
                    time.sleep(15)
                
            except KeyboardInterrupt:
                logger.info("Stopping demo webhook...")
                break
            except Exception as e:
                logger.error(f"Error in demo cycle: {e}")
                time.sleep(10)  # Wait before retrying
        
        logger.info("Demo webhook completed successfully!")

def main():
    """Main function to run the demo outgoing webhook"""
    webhook = DemoOutgoingWebhook()
    
    try:
        logger.info("Starting Demo Outgoing Webhook...")
        webhook.run_demo()
    except KeyboardInterrupt:
        logger.info("Demo Outgoing Webhook stopped by user")
    except Exception as e:
        logger.error(f"Demo Outgoing Webhook error: {e}")

if __name__ == "__main__":
    main()
