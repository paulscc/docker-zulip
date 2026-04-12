#!/usr/bin/env python3
"""
Summary Notification Bot
Sends generated summaries to users via Zulip
"""

import json
import time
import threading
from datetime import datetime
from typing import Dict, List, Any
from kafka import KafkaConsumer
from zulip import Client
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

class SummaryNotificationBot:
    """Bot that sends summaries to users"""
    
    def __init__(self, zulip_config: Dict[str, Any], kafka_config: Dict[str, Any]):
        self.zulip_config = zulip_config
        self.kafka_config = kafka_config
        self.running = False
        
        # Initialize Zulip Client
        self.zulip_client = Client(
            email=zulip_config['email'],
            api_key=zulip_config['api_key'],
            site=zulip_config['server_url']
        )
        
        # Initialize Kafka Consumer
        self.consumer = KafkaConsumer(
            'summary_results',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='summary_notification_group',
            auto_offset_reset='latest'
        )
        
        # User preferences (could be loaded from database)
        self.user_preferences = {}
        self.default_preferences = {
            'summary_interval': 'both',  # 'time', 'count', 'both'
            'min_messages': 5,
            'max_messages': 50,
            'streams': [],  # Empty means all streams
            'notification_type': 'private'  # 'private' or 'stream'
        }
        
        print("Summary Notification Bot initialized")
    
    def start_notifications(self):
        """Start listening for summary results"""
        self.running = True
        print("Starting summary notifications...")
        
        # Start notification thread
        self.notification_thread = threading.Thread(target=self._process_summary_results)
        self.notification_thread.daemon = True
        self.notification_thread.start()
        
        print("Summary notifications started")
    
    def stop_notifications(self):
        """Stop notifications"""
        self.running = False
        if hasattr(self, 'notification_thread'):
            self.notification_thread.join(timeout=5)
        print("Stopped summary notifications")
    
    def _process_summary_results(self):
        """Process summary results from Kafka"""
        try:
            while self.running:
                # Poll for messages
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        try:
                            self._handle_summary_result(message.key, message.value)
                        except Exception as e:
                            print(f"Error processing summary result: {e}")
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except Exception as e:
            print(f"Error in summary result processing: {e}")
    
    def _handle_summary_result(self, stream_topic: str, summary_data: Dict[str, Any]):
        """Handle a single summary result"""
        try:
            print(f"Processing summary result for {stream_topic}")
            
            # Get users who should receive this summary
            users_to_notify = self._get_users_to_notify(stream_topic, summary_data)
            
            # Send summary to each user
            for user_email in users_to_notify:
                self._send_summary_to_user(user_email, stream_topic, summary_data)
            
            # Also send to summary stream if configured
            if self._should_send_to_summary_stream(stream_topic):
                self._send_summary_to_stream(stream_topic, summary_data)
                
        except Exception as e:
            print(f"Error handling summary result for {stream_topic}: {e}")
    
    def _get_users_to_notify(self, stream_topic: str, summary_data: Dict[str, Any]) -> List[str]:
        """Get list of users who should receive the summary"""
        users_to_notify = []
        
        # For now, notify all active users (in real implementation, this would be based on user preferences)
        try:
            # Get users who have access to this stream
            stream_name = stream_topic.split('/')[0] if '/' in stream_topic else stream_topic
            
            # Get stream members
            response = self.zulip_client.get_stream_members(stream_name)
            
            if response['result'] == 'success':
                for member in response['members']:
                    user_email = member.get('email')
                    if user_email and user_email != self.zulip_config['email']:
                        # Check user preferences
                        if self._user_wants_summary(user_email, stream_topic, summary_data):
                            users_to_notify.append(user_email)
            
        except Exception as e:
            print(f"Error getting users to notify: {e}")
            # Fallback: send to admin users
            users_to_notify = ['admin@example.com']  # Replace with actual admin email
        
        return users_to_notify
    
    def _user_wants_summary(self, user_email: str, stream_topic: str, summary_data: Dict[str, Any]) -> bool:
        """Check if user wants to receive this summary"""
        # Get user preferences
        prefs = self.user_preferences.get(user_email, self.default_preferences)
        
        # Check if user is subscribed to this stream
        if prefs['streams'] and stream_topic not in prefs['streams']:
            return False
        
        # Check message count threshold
        if summary_data['message_count'] < prefs['min_messages']:
            return False
        
        # Check trigger type preference
        if prefs['summary_interval'] == 'time' and summary_data['trigger_type'] != 'time_interval':
            return False
        elif prefs['summary_interval'] == 'count' and summary_data['trigger_type'] != 'message_count':
            return False
        
        return True
    
    def _send_summary_to_user(self, user_email: str, stream_topic: str, summary_data: Dict[str, Any]):
        """Send summary to a specific user via private message"""
        try:
            message = self._format_summary_message(stream_topic, summary_data, is_private=True)
            
            result = self.zulip_client.send_message({
                'type': 'private',
                'to': user_email,
                'content': message
            })
            
            if result['result'] == 'success':
                print(f"Sent summary to {user_email}")
            else:
                print(f"Failed to send summary to {user_email}: {result.get('msg', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error sending summary to {user_email}: {e}")
    
    def _send_summary_to_stream(self, stream_topic: str, summary_data: Dict[str, Any]):
        """Send summary to a dedicated summary stream"""
        try:
            message = self._format_summary_message(stream_topic, summary_data, is_private=False)
            
            # Send to summary stream
            result = self.zulip_client.send_message({
                'type': 'stream',
                'to': 'resumenes',  # Summary stream name
                'topic': f"Resumen: {stream_topic}",
                'content': message
            })
            
            if result['result'] == 'success':
                print(f"Sent summary to stream resumenes")
            else:
                print(f"Failed to send summary to stream: {result.get('msg', 'Unknown error')}")
                
        except Exception as e:
            print(f"Error sending summary to stream: {e}")
    
    def _should_send_to_summary_stream(self, stream_topic: str) -> bool:
        """Check if summary should also be sent to summary stream"""
        # For now, send all summaries to summary stream
        return True
    
    def _format_summary_message(self, stream_topic: str, summary_data: Dict[str, Any], is_private: bool) -> str:
        """Format the summary message"""
        summary = summary_data['summary']
        trigger_type = summary_data['trigger_type']
        message_count = summary_data['message_count']
        summary_type = summary_data.get('summary_type', 'gemini')
        
        # Format header
        if is_private:
            header = f"## Resumen Automático de Mensajes No Leídos"
        else:
            header = f"## Resumen Automático"
        
        # Format trigger info
        trigger_text = {
            'time_interval': 'Período de tiempo',
            'message_count': 'Volumen de mensajes'
        }.get(trigger_type, 'Automático')
        
        # Format message
        formatted_message = f"""{header}

**Canal:** {stream_topic}
**Mensajes:** {message_count}
**Disparador:** {trigger_text}
**Generado por:** {summary_type.upper()}

{summary}

---
*Este resumen fue generado automáticamente usando IA. Si no quieres recibir estos resúmenes, configura tus preferencias en el bot de resúmenes.*
"""
        
        return formatted_message
    
    def set_user_preferences(self, user_email: str, preferences: Dict[str, Any]):
        """Set user preferences for summaries"""
        self.user_preferences[user_email] = {**self.default_preferences, **preferences}
        print(f"Updated preferences for {user_email}")
    
    def get_user_preferences(self, user_email: str) -> Dict[str, Any]:
        """Get user preferences"""
        return self.user_preferences.get(user_email, self.default_preferences)

def main():
    """Main function to run the summary notification bot"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Summary Notification Bot')
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
    
    # Create and start bot
    bot = SummaryNotificationBot(zulip_config, kafka_config)
    
    try:
        bot.start_notifications()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
        bot.stop_notifications()
    except Exception as e:
        print(f"Error: {e}")
        bot.stop_notifications()

if __name__ == '__main__':
    main()
