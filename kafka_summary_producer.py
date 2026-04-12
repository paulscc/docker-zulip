#!/usr/bin/env python3
"""
Kafka Producer for Zulip Messages
Captures messages from Zulip and sends them to Kafka for processing
"""

import json
import time
import os
import threading
from datetime import datetime
from typing import Dict, List, Any
from kafka import KafkaProducer
from zulip import Client
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

class ZulipKafkaProducer:
    """Producer that captures Zulip messages and sends them to Kafka"""
    
    def __init__(self, zulip_config: Dict[str, Any], kafka_config: Dict[str, Any]):
        self.zulip_config = zulip_config
        self.kafka_config = kafka_config
        self.running = False
        
        # Initialize Kafka Producer
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        # Initialize Zulip Client
        self.zulip_client = Client(
            email=zulip_config['email'],
            api_key=zulip_config['api_key'],
            site=zulip_config['server_url']
        )
        
        # Topics
        self.topics = {
            'unread_messages': 'unread_messages',
            'message_events': 'message_events',
            'summary_triggers': 'summary_triggers'
        }
        
        # Message tracking
        self.processed_messages = set()
        self.message_buffer = {}
        self.last_check_time = datetime.now()
        
    def start_monitoring(self):
        """Start monitoring Zulip for new messages"""
        self.running = True
        print("Starting Zulip message monitoring...")
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_messages)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        # Start periodic summary trigger
        self.summary_thread = threading.Thread(target=self._periodic_summary_trigger)
        self.summary_thread.daemon = True
        self.summary_thread.start()
        
    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        if hasattr(self, 'summary_thread'):
            self.summary_thread.join(timeout=5)
        print("Stopped Zulip message monitoring")
    
    def _monitor_messages(self):
        """Monitor Zulip for new messages using events API"""
        try:
            # Register for message events
            register_data = {
                'event_types': ['message'],
                'all_public_streams': True
            }
            
            response = self.zulip_client.register(register_data)
            
            if response['result'] == 'success':
                queue_id = response['queue_id']
                last_event_id = response['last_event_id']
                
                print(f"Registered for message events. Queue ID: {queue_id}")
                
                while self.running:
                    try:
                        # Get new events
                        events_response = self.zulip_client.get_events(
                            queue_id=queue_id,
                            last_event_id=last_event_id
                        )
                        
                        if events_response['result'] == 'success':
                            for event in events_response['events']:
                                if event['type'] == 'message' and event['message']:
                                    self._process_message_event(event)
                                    last_event_id = event['id']
                        
                        time.sleep(1)  # Poll every second
                        
                    except Exception as e:
                        print(f"Error polling events: {e}")
                        time.sleep(5)
                        
            else:
                print(f"Failed to register for events: {response.get('msg', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error in message monitoring: {e}")
    
    def _process_message_event(self, event: Dict[str, Any]):
        """Process a single message event"""
        try:
            message = event['message']
            message_id = message['id']
            
            # Avoid processing duplicate messages
            if message_id in self.processed_messages:
                return
            
            self.processed_messages.add(message_id)
            
            # Create Kafka message
            kafka_message = {
                'message_id': message_id,
                'stream': message.get('stream_id'),
                'stream_name': message.get('display_recipient', ''),
                'topic': message.get('subject', ''),
                'sender_email': message.get('sender_email', ''),
                'sender_full_name': message.get('sender_full_name', ''),
                'content': message.get('content', ''),
                'timestamp': message.get('timestamp', 0),
                'message_type': message.get('type', 'stream'),
                'event_timestamp': datetime.now().isoformat(),
                'read_status': 'unread'
            }
            
            # Send to Kafka topics
            self.producer.send(
                self.topics['unread_messages'],
                key=str(message_id),
                value=kafka_message
            )
            
            self.producer.send(
                self.topics['message_events'],
                key=str(message_id),
                value={
                    **kafka_message,
                    'event_type': 'new_message'
                }
            )
            
            # Buffer for summary triggering
            self._buffer_message_for_summary(kafka_message)
            
            print(f"Sent message {message_id} to Kafka: {kafka_message['stream_name']}/{kafka_message['topic']}")
            
        except Exception as e:
            print(f"Error processing message event: {e}")
    
    def _buffer_message_for_summary(self, message: Dict[str, Any]):
        """Buffer messages for summary triggering"""
        stream_topic = f"{message['stream_name']}/{message['topic']}"
        
        if stream_topic not in self.message_buffer:
            self.message_buffer[stream_topic] = []
        
        self.message_buffer[stream_topic].append(message)
        
        # Trigger summary if buffer reaches threshold
        if len(self.message_buffer[stream_topic]) >= 10:  # Configurable threshold
            self._trigger_summary_for_stream(stream_topic)
    
    def _trigger_summary_for_stream(self, stream_topic: str):
        """Trigger summary generation for a specific stream/topic"""
        messages = self.message_buffer.get(stream_topic, [])
        
        if messages:
            summary_trigger = {
                'trigger_type': 'message_count',
                'stream_topic': stream_topic,
                'message_count': len(messages),
                'oldest_message': min(msg['timestamp'] for msg in messages),
                'newest_message': max(msg['timestamp'] for msg in messages),
                'trigger_timestamp': datetime.now().isoformat(),
                'messages': messages[-10:]  # Last 10 messages
            }
            
            self.producer.send(
                self.topics['summary_triggers'],
                key=stream_topic,
                value=summary_trigger
            )
            
            # Clear buffer for this stream
            self.message_buffer[stream_topic] = []
            
            print(f"Triggered summary for {stream_topic}: {len(messages)} messages")
    
    def _periodic_summary_trigger(self):
        """Trigger summaries based on time intervals"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check if 5 minutes have passed since last check
                if (current_time - self.last_check_time).total_seconds() >= 300:  # 5 minutes
                    for stream_topic, messages in self.message_buffer.items():
                        if messages:  # Only trigger if there are messages
                            summary_trigger = {
                                'trigger_type': 'time_interval',
                                'stream_topic': stream_topic,
                                'message_count': len(messages),
                                'oldest_message': min(msg['timestamp'] for msg in messages),
                                'newest_message': max(msg['timestamp'] for msg in messages),
                                'trigger_timestamp': current_time.isoformat(),
                                'messages': messages
                            }
                            
                            self.producer.send(
                                self.topics['summary_triggers'],
                                key=stream_topic,
                                value=summary_trigger
                            )
                    
                    # Clear all buffers and update last check time
                    self.message_buffer.clear()
                    self.last_check_time = current_time
                    
                    print(f"Triggered periodic summaries for {len(self.message_buffer)} streams")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"Error in periodic summary trigger: {e}")
                time.sleep(60)
    
    def get_unread_messages_for_user(self, user_email: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get unread messages for a specific user"""
        try:
            # Get user's unread messages
            request = {
                'anchor': 'newest',
                'num_before': limit,
                'num_after': 0,
                'narrow': [
                    {'operator': 'is', 'operand': 'unread'}
                ]
            }
            
            response = self.zulip_client.get_messages(request)
            
            if response['result'] == 'success':
                messages = []
                for msg in response['messages']:
                    messages.append({
                        'message_id': msg['id'],
                        'stream': msg.get('stream_id'),
                        'stream_name': msg.get('display_recipient', ''),
                        'topic': msg.get('subject', ''),
                        'sender_email': msg.get('sender_email', ''),
                        'sender_full_name': msg.get('sender_full_name', ''),
                        'content': msg.get('content', ''),
                        'timestamp': msg.get('timestamp', 0),
                        'message_type': msg.get('type', 'stream')
                    })
                
                return messages
            else:
                print(f"Error getting unread messages: {response.get('msg', 'Unknown error')}")
                return []
                
        except Exception as e:
            print(f"Error getting unread messages for user {user_email}: {e}")
            return []

def main():
    """Main function to run the Kafka producer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Zulip Kafka Producer for Message Summaries')
    parser.add_argument('--zulip-email', required=True, help='Zulip bot email')
    parser.add_argument('--zulip-api-key', required=True, help='Zulip bot API key')
    parser.add_argument('--zulip-server', required=True, help='Zulip server URL')
    parser.add_argument('--kafka-servers', default='localhost:9092', help='Kafka bootstrap servers')
    
    args = parser.parse_args()
    
    # Configuration
    zulip_config = {
        'email': args.zulip_email,
        'api_key': args.zulip_api_key,
        'server_url': args.zulip_server
    }
    
    kafka_config = {
        'bootstrap_servers': args.kafka_servers.split(',')
    }
    
    # Create and start producer
    producer = ZulipKafkaProducer(zulip_config, kafka_config)
    
    try:
        producer.start_monitoring()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
        producer.stop_monitoring()
    except Exception as e:
        print(f"Error: {e}")
        producer.stop_monitoring()

if __name__ == '__main__':
    main()
