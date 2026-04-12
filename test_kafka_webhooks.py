#!/usr/bin/env python3
"""
Test Kafka Webhooks System
Test the complete webhook flow with Kafka: outgoing -> Kafka -> processor -> Kafka -> incoming
"""

import requests
import json
import logging
import time
import subprocess
from datetime import datetime
from typing import Dict, List

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaWebhookTester:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize Kafka webhook tester"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_unread = "zulip-unread-messages"
        self.kafka_topic_summaries = "zulip-summaries"
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
    
    def test_kafka_connection(self) -> bool:
        """Test if Kafka is accessible"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--list"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
                logger.info(f"Kafka accessible. Topics: {topics}")
                return True
            else:
                logger.error(f"Kafka not accessible: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Kafka connection: {e}")
            return False
    
    def test_kafka_topics(self) -> bool:
        """Test if required Kafka topics exist"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--list"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
                
                if self.kafka_topic_unread in topics and self.kafka_topic_summaries in topics:
                    logger.info("All required Kafka topics exist")
                    return True
                else:
                    logger.error(f"Missing topics. Required: {self.kafka_topic_unread}, {self.kafka_topic_summaries}")
                    logger.error(f"Available: {topics}")
                    return False
            else:
                logger.error(f"Error listing topics: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Kafka topics: {e}")
            return False
    
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
                return status.get("kafka_status") == "available" and status.get("ollama_status") == "available"
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
    
    def send_test_unread_to_kafka(self) -> bool:
        """Send test unread messages to Kafka topic"""
        try:
            test_payload = {
                "stream": "webhooks",
                "topic": "prueba-kafka",
                "messages": [
                    {
                        "content": "Este es un mensaje de prueba para el sistema Kafka",
                        "sender_full_name": "Usuario Test 1",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "content": "Otro mensaje de prueba para verificar el funcionamiento con Kafka",
                        "sender_full_name": "Usuario Test 2",
                        "timestamp": datetime.now().isoformat()
                    },
                    {
                        "content": "Tercer mensaje para tener suficiente contenido y generar un buen resumen",
                        "sender_full_name": "Usuario Test 3",
                        "timestamp": datetime.now().isoformat()
                    }
                ]
            }
            
            response = requests.post(
                f"{self.service_url}/kafka/send-unread",
                json=test_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info("Test unread messages sent to Kafka successfully")
                logger.info(f"Response: {response.json()}")
                return True
            else:
                logger.error(f"Test unread messages failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test unread messages: {e}")
            return False
    
    def send_test_message_to_zulip(self) -> bool:
        """Send a test message to Zulip to trigger the webhook"""
        try:
            url = f"{self.outgoing_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.outgoing_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            test_message = f"""Mensaje de prueba para sistema Kafka

Enviado a las: {datetime.now().strftime('%H:%M:%S')}
Stream: webhooks
Topic: prueba-kafka

Este mensaje será procesado por el sistema:
1. Outgoing webhook detecta el trigger
2. Envía mensajes a Kafka topic 'zulip-unread-messages'
3. Kafka processor genera resumen con Ollama
4. Publica resumen en Kafka topic 'zulip-summaries'
5. Incoming webhook consume y publica en Zulip
"""
            
            payload = {
                "type": "stream",
                "to": "webhooks",
                "topic": "prueba-kafka",
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
    
    def check_kafka_messages(self, topic: str, timeout: int = 10) -> List[str]:
        """Check messages in a Kafka topic"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-console-consumer",
                "--bootstrap-server", "localhost:9092",
                "--topic", topic,
                "--from-beginning",
                "--timeout-ms", str(timeout * 1000)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 5)
            
            if result.returncode == 0 and result.stdout.strip():
                messages = result.stdout.strip().split('\n')
                logger.info(f"Found {len(messages)} messages in topic '{topic}'")
                return messages
            else:
                logger.info(f"No messages found in topic '{topic}'")
                return []
                
        except Exception as e:
            logger.error(f"Error checking Kafka messages: {e}")
            return []
    
    def run_complete_test(self):
        """Run complete Kafka webhook system test"""
        logger.info("Starting complete Kafka webhook system test...")
        print("\n" + "="*70)
        print("KAFKA WEBHOOK SYSTEM TEST")
        print("="*70)
        
        # Test 1: Kafka connection
        print("\n1. Testing Kafka connection...")
        if not self.test_kafka_connection():
            print("   FAILED: Kafka is not accessible")
            return False
        print("   PASSED: Kafka is accessible")
        
        # Test 2: Kafka topics
        print("\n2. Testing Kafka topics...")
        if not self.test_kafka_topics():
            print("   FAILED: Required Kafka topics not found")
            print("   Run: python setup_kafka_topics.py")
            return False
        print("   PASSED: All required Kafka topics exist")
        
        # Test 3: Service health
        print("\n3. Testing webhook service health...")
        if not self.test_service_health():
            print("   FAILED: Webhook service is not running")
            print("   Start with: python webhook_service_kafka.py")
            return False
        print("   PASSED: Webhook service is running")
        
        # Test 4: Service status
        print("\n4. Testing service status (Ollama + Kafka)...")
        if not self.test_service_status():
            print("   WARNING: Service status check failed")
            print("   Ensure Ollama is running and Kafka topics exist")
        else:
            print("   PASSED: Service, Ollama, and Kafka are available")
        
        # Test 5: Bot connections
        print("\n5. Testing bot connections...")
        outgoing_ok = self.test_outgoing_webhook()
        incoming_ok = self.test_incoming_webhook()
        
        if not outgoing_ok:
            print("   FAILED: Outgoing webhook bot (xxx-bot)")
            return False
        if not incoming_ok:
            print("   FAILED: Incoming webhook bot (zzz-bot)")
            return False
        print("   PASSED: Both bots are connected")
        
        # Test 6: Send test data to Kafka
        print("\n6. Sending test unread messages to Kafka...")
        if not self.send_test_unread_to_kafka():
            print("   FAILED: Could not send test messages to Kafka")
            return False
        print("   PASSED: Test messages sent to Kafka")
        
        # Test 7: Check Kafka topics for messages
        print("\n7. Checking Kafka topics for messages...")
        time.sleep(2)  # Wait for processing
        
        unread_messages = self.check_kafka_messages(self.kafka_topic_unread, timeout=5)
        summary_messages = self.check_kafka_messages(self.kafka_topic_summaries, timeout=5)
        
        if unread_messages:
            print(f"   PASSED: Found {len(unread_messages)} messages in unread topic")
        else:
            print("   WARNING: No messages found in unread topic")
        
        if summary_messages:
            print(f"   PASSED: Found {len(summary_messages)} messages in summary topic")
        else:
            print("   WARNING: No summaries found in summary topic")
            print("   Note: Kafka processor may not be running")
        
        # Test 8: Send test message to Zulip
        print("\n8. Sending test message to Zulip...")
        if not self.send_test_message_to_zulip():
            print("   FAILED: Could not send test message to Zulip")
            return False
        print("   PASSED: Test message sent to Zulip")
        
        print("\n" + "="*70)
        print("KAFKA WEBHOOK SYSTEM TEST COMPLETED!")
        print("="*70)
        print("\nTest Results:")
        print(f"- Kafka Connection: {'PASSED' if self.test_kafka_connection() else 'FAILED'}")
        print(f"- Kafka Topics: {'PASSED' if self.test_kafka_topics() else 'FAILED'}")
        print(f"- Webhook Service: {'PASSED' if self.test_service_health() else 'FAILED'}")
        print(f"- Bot Connections: {'PASSED' if outgoing_ok and incoming_ok else 'FAILED'}")
        print(f"- Test Messages: {'PASSED' if unread_messages else 'PARTIAL'}")
        print(f"- Test Summaries: {'PASSED' if summary_messages else 'PARTIAL'}")
        
        print("\nTo run the complete Kafka system:")
        print("1. python webhook_service_kafka.py")
        print("2. python kafka_summary_processor.py")
        print("3. python outgoing_webhook.py")
        print("4. python incoming_webhook.py")
        print("\nOr use the standalone processors:")
        print("- Outgoing: python outgoing_webhook.py (sends to Kafka)")
        print("- Processor: python kafka_summary_processor.py (consumes & processes)")
        print("- Incoming: python incoming_webhook.py (consumes summaries)")
        print("="*70)
        
        return True

def main():
    """Main function to run Kafka webhook tests"""
    tester = KafkaWebhookTester()
    
    try:
        success = tester.run_complete_test()
        if not success:
            print("\nSome tests failed. Please check the logs above.")
            return False
            
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
        return False
    except Exception as e:
        logger.error(f"Test error: {e}")
        print(f"\nTest failed with error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
