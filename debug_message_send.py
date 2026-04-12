#!/usr/bin/env python3
"""
Debug Message Send
Depura el envío de mensajes a Zulip API
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DebugMessageSend:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize debug message send"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("xxx-bot")
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
    
    def test_simple_message(self):
        """Test sending a simple message"""
        print("Testing simple message...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Simple message
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "debug",
                "content": "Test message from debug script"
            }
            
            print(f"URL: {url}")
            print(f"Auth: {self.monitor_bot['email']}:***")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            response = requests.post(url, auth=auth, json=payload, verify=False)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Message ID: {result.get('id', 'Unknown')}")
                return True
            else:
                print(f"Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_with_data_param(self):
        """Test sending with data parameter instead of json"""
        print("Testing with data parameter...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Simple message
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "debug-data",
                "content": "Test message with data parameter"
            }
            
            print(f"Using data parameter...")
            
            response = requests.post(url, auth=auth, data=json.dumps(payload), 
                                   headers={'Content-Type': 'application/json'}, 
                                   verify=False)
            
            print(f"Status Code: {response.status_code}")
            print(f"Response Body: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"Success! Message ID: {result.get('id', 'Unknown')}")
                return True
            else:
                print(f"Failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def test_different_payloads(self):
        """Test different payload formats"""
        print("Testing different payload formats...")
        
        payloads = [
            # Format 1: Basic
            {
                "type": "stream",
                "to": self.target_stream,
                "topic": "debug-1",
                "content": "Basic format test"
            },
            # Format 2: With stream_id
            {
                "type": "stream",
                "to": self.target_stream,
                "topic": "debug-2", 
                "content": "Format 2 test"
            },
            # Format 3: Minimal
            {
                "type": "stream",
                "to": self.target_stream,
                "topic": "debug-3",
                "content": "Minimal test"
            }
        ]
        
        for i, payload in enumerate(payloads, 1):
            print(f"\nTesting payload {i}:")
            print(f"Payload: {json.dumps(payload, indent=2)}")
            
            try:
                server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
                url = f"{server_url}/api/v1/messages"
                
                from requests.auth import HTTPBasicAuth
                auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
                
                response = requests.post(url, auth=auth, json=payload, verify=False)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text}")
                
                if response.status_code == 200:
                    print(f"Payload {i}: SUCCESS")
                else:
                    print(f"Payload {i}: FAILED")
                
            except Exception as e:
                print(f"Payload {i}: ERROR - {e}")

def main():
    """Main function"""
    debug = DebugMessageSend()
    
    print("="*60)
    print("DEBUG MESSAGE SEND")
    print("="*60)
    
    # Test 1: Simple message
    print("\n1. Testing simple message...")
    debug.test_simple_message()
    
    print("\n" + "="*60)
    
    # Test 2: Data parameter
    print("\n2. Testing with data parameter...")
    debug.test_with_data_param()
    
    print("\n" + "="*60)
    
    # Test 3: Different payloads
    print("\n3. Testing different payloads...")
    debug.test_different_payloads()
    
    print("\n" + "="*60)
    print("DEBUG COMPLETED")

if __name__ == "__main__":
    main()
