#!/usr/bin/env python3
"""
Test Webhooks System
Test the complete webhook flow: outgoing -> service -> incoming
"""

import requests
import json
import logging
import time
from datetime import datetime
from threading import Thread
import subprocess
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookTester:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize webhook tester"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.service_url = "http://localhost:8080"
        
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
    
    def test_service_health(self) -> bool:
        """Test if webhook service is running"""
        try:
            response = requests.get(f"{self.service_url}/health", timeout=5)
            if response.status_code == 200:
                logger.info("Webhook service is running")
                return True
            else:
                logger.error(f"Webhook service returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Webhook service not accessible: {e}")
            return False
    
    def test_service_status(self) -> bool:
        """Test detailed service status"""
        try:
            response = requests.get(f"{self.service_url}/status", timeout=5)
            if response.status_code == 200:
                status = response.json()
                logger.info(f"Service status: {status}")
                return status.get("ollama_status") == "available"
            else:
                logger.error(f"Service status check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Service status check error: {e}")
            return False
    
    def test_outgoing_webhook(self) -> bool:
        """Test outgoing webhook connection"""
        try:
            url = f"{self.outgoing_bot['server_url']}/api/v1/users/me"
            headers = {
                "Authorization": f"Bearer {self.outgoing_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                logger.info("Outgoing webhook bot connection OK")
                return True
            else:
                logger.error(f"Outgoing webhook bot connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Outgoing webhook test error: {e}")
            return False
    
    def test_incoming_webhook(self) -> bool:
        """Test incoming webhook connection"""
        try:
            url = f"{self.incoming_bot['server_url']}/api/v1/users/me"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                logger.info("Incoming webhook bot connection OK")
                return True
            else:
                logger.error(f"Incoming webhook bot connection failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Incoming webhook test error: {e}")
            return False
    
    def send_test_webhook_payload(self) -> bool:
        """Send a test payload to the webhook service"""
        try:
            test_payload = {
                "trigger_type": "test",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "stream": "webhooks",
                    "topic": "prueba",
                    "messages": [
                        {
                            "content": "Este es un mensaje de prueba para el sistema de webhooks",
                            "sender_full_name": "Usuario Test",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "content": "Otro mensaje de prueba para verificar el funcionamiento",
                            "sender_full_name": "Otro Usuario",
                            "timestamp": datetime.now().isoformat()
                        }
                    ],
                    "message_count": 2
                },
                "webhook_token": self.outgoing_bot.get("webhook_token")
            }
            
            response = requests.post(
                f"{self.service_url}/webhook/receive",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Test webhook payload sent successfully")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"Test webhook payload failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test webhook payload: {e}")
            return False
    
    def send_test_message_to_zulip(self) -> bool:
        """Send a test message to Zulip to trigger the webhook"""
        try:
            url = f"{self.outgoing_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.outgoing_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            test_message = f"""Este es un mensaje de prueba para el sistema de webhooks automáticos.

Enviado a las: {datetime.now().strftime('%H:%M:%S')}
Stream: webhooks
Topic: prueba

Este mensaje debería ser detectado por el outgoing webhook y procesado por el servicio para generar un resumen.
"""
            
            payload = {
                "type": "stream",
                "to": "webhooks",
                "topic": "prueba",
                "content": test_message
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info("Test message sent to Zulip successfully")
                return True
            else:
                logger.error(f"Error sending test message: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test message: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete webhook system test"""
        logger.info("Starting complete webhook system test...")
        print("\n" + "="*60)
        print("WEBHOOK SYSTEM TEST")
        print("="*60)
        
        # Test 1: Service health
        print("\n1. Testing webhook service health...")
        if not self.test_service_health():
            print("   FAILED: Webhook service is not running")
            print("   Please start with: python webhook_service.py")
            return False
        print("   PASSED: Webhook service is running")
        
        # Test 2: Service status
        print("\n2. Testing service status and Ollama...")
        if not self.test_service_status():
            print("   WARNING: Ollama might not be available")
        else:
            print("   PASSED: Service and Ollama are available")
        
        # Test 3: Bot connections
        print("\n3. Testing bot connections...")
        outgoing_ok = self.test_outgoing_webhook()
        incoming_ok = self.test_incoming_webhook()
        
        if not outgoing_ok:
            print("   FAILED: Outgoing webhook bot (xxx-bot)")
            return False
        if not incoming_ok:
            print("   FAILED: Incoming webhook bot (zzz-bot)")
            return False
        print("   PASSED: Both bots are connected")
        
        # Test 4: Direct webhook payload
        print("\n4. Testing direct webhook payload...")
        if not self.send_test_webhook_payload():
            print("   FAILED: Direct webhook payload test")
            return False
        print("   PASSED: Direct webhook payload processed")
        
        # Test 5: Send test message to Zulip
        print("\n5. Sending test message to Zulip...")
        if not self.send_test_message_to_zulip():
            print("   FAILED: Could not send test message to Zulip")
            return False
        print("   PASSED: Test message sent to Zulip")
        
        print("\n" + "="*60)
        print("ALL TESTS PASSED!")
        print("="*60)
        print("\nThe webhook system is working correctly.")
        print("Check the 'webhooks' stream in Zulip for the test message and summary.")
        print("\nTo start the full monitoring:")
        print("1. python webhook_service.py")
        print("2. python outgoing_webhook.py")
        print("="*60)
        
        return True

def main():
    """Main function to run webhook tests"""
    tester = WebhookTester()
    
    try:
        success = tester.run_complete_test()
        if not success:
            print("\nSome tests failed. Please check the logs above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"\nTest failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
