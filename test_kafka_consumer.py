#!/usr/bin/env python3
"""
Simple test script to verify Kafka consumption
"""

from kafka import KafkaConsumer
import json
import time

def test_kafka_consumption():
    """Test consuming messages from Kafka topics"""
    
    topics = ['zulip-summaries', 'zulip-unread-messages']
    
    for topic in topics:
        print(f"\n=== Testing topic: {topic} ===")
        
        try:
            consumer = KafkaConsumer(
                topic,
                bootstrap_servers=['localhost:9092'],
                value_deserializer=lambda x: json.loads(x.decode('utf-8')),
                auto_offset_reset='earliest',
                consumer_timeout_ms=5000
            )
            
            messages = []
            for message in consumer:
                message_data = {
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(message.timestamp / 1000)),
                    'content': message.value,
                    'topic': message.topic,
                    'partition': message.partition,
                    'offset': message.offset
                }
                messages.append(message_data)
                print(f"  Message {len(messages)}: offset {message.offset}")
                
                if len(messages) >= 5:  # Limit to 5 messages for testing
                    break
            
            consumer.close()
            print(f"  Total messages retrieved: {len(messages)}")
            
            if messages:
                print(f"  First message content: {messages[0]['content']}")
            
        except Exception as e:
            print(f"  Error: {e}")

if __name__ == "__main__":
    test_kafka_consumption()
