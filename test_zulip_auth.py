#!/usr/bin/env python3
"""
Test Zulip Authentication
Prueba diferentes métodos de autenticación con Zulip
"""

import requests
import json
import logging
import base64
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ZulipAuthTest:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize Zulip auth test"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("zzz-bot")
        
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
    
    def test_bearer_token(self):
        """Test Bearer token authentication"""
        print("Testing Bearer token authentication...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/users/me"
            headers = {
                "Authorization": f"Bearer {self.monitor_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, verify=False)
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Success! Connected as: {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                print(f"  Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_basic_auth(self):
        """Test HTTP Basic authentication"""
        print("Testing HTTP Basic authentication...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/users/me"
            
            # Create basic auth header
            auth_string = f"{self.monitor_bot['email']}:{self.monitor_bot['api_key']}"
            auth_bytes = auth_string.encode('ascii')
            auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
            
            headers = {
                "Authorization": f"Basic {auth_b64}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, verify=False)
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Success! Connected as: {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                print(f"  Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_api_key_param(self):
        """Test API key as parameter"""
        print("Testing API key as parameter...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/users/me"
            params = {
                "api_key": self.monitor_bot['api_key']
            }
            
            response = requests.get(url, params=params, verify=False)
            
            print(f"  Status: {response.status_code}")
            if response.status_code == 200:
                user_data = response.json()
                print(f"  Success! Connected as: {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                print(f"  Failed: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_different_endpoints(self):
        """Test different endpoints"""
        print("Testing different endpoints...")
        
        endpoints = [
            "/api/v1/users/me",
            "/api/v1/server_settings",
            "/api/v1/streams"
        ]
        
        for endpoint in endpoints:
            print(f"  Testing {endpoint}...")
            
            try:
                server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
                url = f"{server_url}{endpoint}"
                headers = {
                    "Authorization": f"Bearer {self.monitor_bot['api_key']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(url, headers=headers, verify=False)
                
                print(f"    Status: {response.status_code}")
                if response.status_code == 200:
                    print(f"    Success!")
                else:
                    print(f"    Failed: {response.text[:100]}")
                
            except Exception as e:
                print(f"    Error: {e}")
    
    def test_server_urls(self):
        """Test different server URLs"""
        print("Testing different server URLs...")
        
        urls_to_test = [
            "https://localhost:443",
            "http://localhost:9991",
            "https://127.0.0.1.nip.io",
            "http://localhost"
        ]
        
        for url in urls_to_test:
            print(f"  Testing {url}...")
            
            try:
                api_url = f"{url}/api/v1/users/me"
                headers = {
                    "Authorization": f"Bearer {self.monitor_bot['api_key']}",
                    "Content-Type": "application/json"
                }
                
                response = requests.get(api_url, headers=headers, verify=False, timeout=5)
                
                print(f"    Status: {response.status_code}")
                if response.status_code == 200:
                    user_data = response.json()
                    print(f"    Success! Connected as: {user_data.get('full_name', 'Unknown')}")
                    return url  # Return working URL
                else:
                    print(f"    Failed: {response.text[:100]}")
                
            except Exception as e:
                print(f"    Error: {e}")
        
        return None
    
    def run_auth_tests(self):
        """Run all authentication tests"""
        print("="*60)
        print("ZULIP AUTHENTICATION TESTS")
        print("="*60)
        
        print(f"Bot: {self.monitor_bot.get('bot_name', 'Unknown')}")
        print(f"Email: {self.monitor_bot.get('email', 'Unknown')}")
        print(f"Server URL: {self.monitor_bot.get('server_url', 'Unknown')}")
        print(f"API Key: {self.monitor_bot.get('api_key', 'Unknown')[:10]}...")
        print("="*60)
        
        # Test 1: Find working server URL
        print("\n1. Finding working server URL...")
        working_url = self.test_server_urls()
        
        if working_url:
            print(f"\nWorking URL found: {working_url}")
            self.monitor_bot['server_url'] = working_url
        else:
            print("\nNo working URL found!")
            return False
        
        print("\n2. Testing authentication methods...")
        
        # Test 2: Bearer token
        bearer_success = self.test_bearer_token()
        
        # Test 3: Basic auth
        basic_success = self.test_basic_auth()
        
        # Test 4: API key parameter
        param_success = self.test_api_key_param()
        
        print("\n3. Testing different endpoints...")
        self.test_different_endpoints()
        
        # Summary
        print("\n" + "="*60)
        print("AUTHENTICATION TEST SUMMARY")
        print("="*60)
        print(f"Working URL: {working_url}")
        print(f"Bearer Token: {'PASS' if bearer_success else 'FAIL'}")
        print(f"Basic Auth: {'PASS' if basic_success else 'FAIL'}")
        print(f"API Key Param: {'PASS' if param_success else 'FAIL'}")
        
        if bearer_success or basic_success or param_success:
            print("\nAuthentication successful!")
            return True
        else:
            print("\nAll authentication methods failed!")
            return False

def main():
    """Main function"""
    test = ZulipAuthTest()
    
    try:
        success = test.run_auth_tests()
        
        if success:
            print("\nNext step: Test webhook de salida with working authentication")
        else:
            print("\nPlease check Zulip server and bot configuration")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
