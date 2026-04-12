#!/usr/bin/env python3
"""
Test Webhook de Salida
Prueba la extracción de información del canal desarrollo
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WebhookSalidaTest:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize webhook salida test"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("xxx-bot")  # Use webhook_outbound bot
        self.target_stream = "desarrollo"
        
    def load_config(self, config_file: str) -> dict:
        """Load bot configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get_bot_config(self, bot_name: str) -> dict:
        """Get specific bot configuration"""
        for bot in self.config.get("bots", []):
            if bot.get("bot_name") == bot_name:
                return bot
        return {}
    
    def test_zulip_connection(self):
        """Test connection to Zulip API"""
        print("Testing Zulip API connection...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/users/me"
            
            # Use HTTP Basic authentication (email:api_key)
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            response = requests.get(url, auth=auth, verify=False)
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Connected as: {user_data.get('full_name', 'Unknown')}")
                print(f"  Email: {user_data.get('email', 'Unknown')}")
                return True
            else:
                print(f"  Connection failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Connection error: {e}")
            return False
    
    def get_streams(self):
        """Get available streams"""
        print("Getting available streams...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/streams"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            response = requests.get(url, auth=auth, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                streams = data.get("streams", [])
                
                print(f"  Found {len(streams)} streams:")
                for stream in streams:
                    stream_name = stream.get("name", "Unknown")
                    print(f"    - #{stream_name}")
                
                # Check if desarrollo stream exists
                desarrollo_exists = any(stream.get("name") == "desarrollo" for stream in streams)
                print(f"  Desarrollo stream exists: {desarrollo_exists}")
                
                return streams
            else:
                print(f"  Error getting streams: {response.status_code}")
                print(f"  Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"  Error getting streams: {e}")
            return []
    
    def get_desarrollo_messages(self, limit: int = 10):
        """Get messages from desarrollo stream"""
        print(f"Getting last {limit} messages from #desarrollo...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Get messages from desarrollo stream
            params = {
                "type": "stream",
                "stream": self.target_stream,
                "narrow": json.dumps([{"operator": "stream", "operand": self.target_stream}]),
                "num_before": limit,
                "num_after": 0,
                "anchor": "newest"  # Add required anchor parameter
            }
            
            response = requests.get(url, auth=auth, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                
                print(f"  Found {len(messages)} messages:")
                for i, msg in enumerate(messages[-limit:], 1):
                    sender = msg.get("sender_full_name", "Unknown")
                    content = msg.get("content", "")
                    topic = msg.get("subject", "No topic")
                    timestamp = msg.get("timestamp", 0)
                    
                    # Format timestamp
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime('%H:%M:%S')
                    
                    print(f"    {i}. [{time_str}] {sender} in '{topic}':")
                    print(f"       {content[:100]}{'...' if len(content) > 100 else ''}")
                    print()
                
                return messages
            else:
                print(f"  Error getting messages: {response.status_code}")
                print(f"  Response: {response.text}")
                return []
                
        except Exception as e:
            print(f"  Error getting messages: {e}")
            return []
    
    def analyze_message_content(self, messages):
        """Analyze message content for topic changes"""
        print("Analyzing message content...")
        
        if not messages:
            print("  No messages to analyze")
            return
        
        # Technology keywords
        tech_keywords = {
            'programación', 'codigo', 'software', 'desarrollo', 'api', 'base de datos',
            'frontend', 'backend', 'javascript', 'python', 'java', 'react', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'cloud', 'devops', 'git',
            'algoritmo', 'framework', 'libreria', 'bug', 'debug', 'test', 'deploy',
            'servidor', 'cliente', 'microservicios', 'arquitectura', 'seguridad',
            'performance', 'optimización', 'escalabilidad', 'integración'
        }
        
        # Non-tech keywords
        non_tech_keywords = {
            'empresa', 'política', 'salario', 'vacaciones', 'reunión', 'jefe',
            'comida', 'clima', 'deporte', 'noticias', 'personal', 'familia',
            'finanzas', 'bancos', 'impuestos', 'seguro', 'médico', 'salud'
        }
        
        for i, msg in enumerate(messages, 1):
            content = msg.get("content", "").lower()
            sender = msg.get("sender_full_name", "Unknown")
            
            # Count keywords
            tech_count = sum(1 for word in tech_keywords if word in content)
            non_tech_count = sum(1 for word in non_tech_keywords if word in content)
            
            print(f"    {i}. {sender}:")
            print(f"       Tech keywords: {tech_count}, Non-tech keywords: {non_tech_count}")
            
            if tech_count > 0:
                found_tech = [word for word in tech_keywords if word in content]
                print(f"       Tech topics: {', '.join(found_tech[:3])}")
            
            if non_tech_count > 0:
                found_non_tech = [word for word in non_tech_keywords if word in content]
                print(f"       Non-tech topics: {', '.join(found_non_tech[:3])}")
            
            print()
    
    def test_topic_change_detection(self, messages):
        """Test topic change detection logic"""
        print("Testing topic change detection...")
        
        if len(messages) < 2:
            print("  Need at least 2 messages to test topic changes")
            return
        
        # Simple topic change detection
        def extract_keywords(content):
            words = content.lower().split()
            tech_words = [word for word in words if word in ['api', 'python', 'docker', 'react', 'database']]
            non_tech_words = [word for word in words if word in ['empresa', 'política', 'salario', 'reunión']]
            return set(tech_words + non_tech_words)
        
        for i in range(1, len(messages)):
            prev_msg = messages[i-1]
            curr_msg = messages[i]
            
            prev_keywords = extract_keywords(prev_msg.get("content", ""))
            curr_keywords = extract_keywords(curr_msg.get("content", ""))
            
            # Calculate similarity
            if prev_keywords and curr_keywords:
                intersection = prev_keywords.intersection(curr_keywords)
                union = prev_keywords.union(curr_keywords)
                similarity = len(intersection) / len(union) if union else 0
                
                prev_sender = prev_msg.get("sender_full_name", "Unknown")
                curr_sender = curr_msg.get("sender_full_name", "Unknown")
                
                print(f"    {prev_sender} -> {curr_sender}:")
                print(f"       Similarity: {similarity:.2f}")
                print(f"       Previous: {list(prev_keywords)}")
                print(f"       Current: {list(curr_keywords)}")
                
                if similarity < 0.3:
                    print(f"       *** TOPIC CHANGE DETECTED ***")
                
                print()
    
    def run_complete_test(self):
        """Run complete webhook salida test"""
        print("="*60)
        print("WEBHOOK DE SALIDA TEST - CANAL DESARROLLO")
        print("="*60)
        
        # Test 1: Connection
        if not self.test_zulip_connection():
            print("\nConnection test failed. Stopping.")
            return False
        
        print()
        
        # Test 2: Get streams
        streams = self.get_streams()
        if not streams:
            print("\nNo streams found. Stopping.")
            return False
        
        print()
        
        # Test 3: Get desarrollo messages
        messages = self.get_desarrollo_messages(limit=5)
        if not messages:
            print("\nNo messages found in desarrollo stream. Stopping.")
            return False
        
        print()
        
        # Test 4: Analyze content
        self.analyze_message_content(messages)
        
        # Test 5: Topic change detection
        self.test_topic_change_detection(messages)
        
        print("\n" + "="*60)
        print("WEBHOOK SALIDA TEST COMPLETED!")
        print("="*60)
        print(f"Successfully extracted information from #{self.target_stream}")
        print(f"Found {len(messages)} messages")
        print("Content analysis completed")
        print("Topic change detection logic tested")
        print("="*60)
        
        return True

def main():
    """Main function"""
    test = WebhookSalidaTest()
    
    try:
        test.run_complete_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
