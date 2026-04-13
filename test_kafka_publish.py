#!/usr/bin/env python3
"""
Test Kafka publishing for chat_summary_processor
"""

import json
import logging
from datetime import datetime
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_kafka_connection():
    """Test Kafka connection and publishing"""
    try:
        # Initialize Kafka producer
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        logger.info("Kafka producer initialized successfully")
        
        # Test message
        test_payload = {
            "message_type": "test_summary",
            "timestamp": datetime.now().isoformat(),
            "stream": "test",
            "topic": "test",
            "summary": "Test message from chat_summary_processor",
            "message_count": 1,
            "message_links": [],
            "summary_period_minutes": 1,
            "processed_at": datetime.now().isoformat(),
            "server_url": "https://localhost:443",
            "processing_mode": "test"
        }
        
        # Send to Kafka
        try:
            key = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            future = producer.send(
                "zulip-summaries",
                key=key,
                value=test_payload
            )
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=30)
            
            logger.info(f"Test message published successfully!")
            logger.info(f"Topic: {record_metadata.topic}")
            logger.info(f"Partition: {record_metadata.partition}")
            logger.info(f"Offset: {record_metadata.offset}")
            
            producer.close()
            return True
            
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error initializing Kafka producer: {e}")
        return False

def test_chat_summary_processor_logic():
    """Test the logic from chat_summary_processor"""
    try:
        # Simulate the payload that chat_summary_processor creates
        demo_messages = [
            {
                "id": 1001,
                "content": "Demo: Actividad reciente en test/test - Sistema de resúmenes funcionando",
                "sender_full_name": "Demo Bot",
                "timestamp": datetime.now().timestamp() - 240,
                "direct_link": "https://localhost:443/#narrow/stream/test/topic/test/near/demo1"
            }
        ]
        
        # Create the exact same payload as chat_summary_processor
        payload = {
            "message_type": "chat_summary",
            "timestamp": datetime.now().isoformat(),
            "stream": "test",
            "topic": "test",
            "summary": "Test summary from chat_summary_processor logic",
            "message_count": len(demo_messages),
            "message_links": [
                {
                    "id": demo_messages[0]["id"],
                    "sender": demo_messages[0]["sender_full_name"],
                    "content_preview": demo_messages[0]["content"][:50] + "...",
                    "direct_link": demo_messages[0]["direct_link"],
                    "timestamp": demo_messages[0]["timestamp"]
                }
            ],
            "summary_period_minutes": 5,
            "processed_at": datetime.now().isoformat(),
            "server_url": "https://localhost:443"
        }
        
        # Initialize Kafka producer
        producer = KafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Send to Kafka
        try:
            key = f"test-{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            future = producer.send(
                "zulip-summaries",
                key=key,
                value=payload
            )
            
            # Wait for the message to be sent
            record_metadata = future.get(timeout=30)
            
            logger.info(f"Chat Summary Processor test message published!")
            logger.info(f"Topic: {record_metadata.topic}")
            logger.info(f"Partition: {record_metadata.partition}")
            logger.info(f"Offset: {record_metadata.offset}")
            
            producer.close()
            return True
            
        except Exception as e:
            logger.error(f"Error sending to Kafka: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Error in test: {e}")
        return False

if __name__ == "__main__":
    logger.info("=== Testing Kafka Connection ===")
    test_kafka_connection()
    
    logger.info("\n=== Testing Chat Summary Processor Logic ===")
    test_chat_summary_processor_logic()
    
    logger.info("\n=== Test Complete ===")
    logger.info("Check Kafka topic 'zulip-summaries' for test messages")
