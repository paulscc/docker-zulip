#!/usr/bin/env python3
"""
Test Form Data Send
Prueba envío de mensajes usando form data (multipart/form-data)
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TestFormDataSend:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize form data test"""
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
    
    def test_form_data_send(self):
        """Test sending message using form data"""
        print("Testing form data send...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Form data
            data = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "form-data-test",
                "content": "Test message using form data"
            }
            
            print(f"URL: {url}")
            print(f"Data: {data}")
            
            response = requests.post(url, auth=auth, data=data, verify=False)
            
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
    
    def test_multipart_form_data(self):
        """Test sending message using multipart form data"""
        print("Testing multipart form data...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Multipart form data
            from requests_toolbelt.multipart.encoder import MultipartEncoder
            
            multipart_data = MultipartEncoder({
                "type": "stream",
                "to": self.target_stream,
                "topic": "multipart-test",
                "content": "Test message using multipart form data"
            })
            
            headers = {
                "Content-Type": multipart_data.content_type
            }
            
            response = requests.post(url, auth=auth, data=multipart_data, headers=headers, verify=False)
            
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
            print("Trying without requests_toolbelt...")
            return self.test_simple_form_data()
    
    def test_simple_form_data(self):
        """Test simple form data without multipart"""
        print("Testing simple form data...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Simple form data
            data = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "simple-form-test",
                "content": "Test message using simple form data"
            }
            
            headers = {
                "Content-Type": "application/x-www-form-urlencoded"
            }
            
            response = requests.post(url, auth=auth, data=data, headers=headers, verify=False)
            
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
            return False

def main():
    """Main function"""
    test = TestFormDataSend()
    
    print("="*60)
    print("TEST FORM DATA SEND")
    print("="*60)
    
    # Test 1: Regular form data
    print("\n1. Testing regular form data...")
    test.test_form_data_send()
    
    print("\n" + "="*60)
    
    # Test 2: Multipart form data
    print("\n2. Testing multipart form data...")
    test.test_multipart_form_data()
    
    print("\n" + "="*60)
    print("FORM DATA TEST COMPLETED")

if __name__ == "__main__":
    main()
