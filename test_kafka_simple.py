#!/usr/bin/env python3
"""
Simple Kafka Webhooks Test
Test the Kafka webhook flow without SSL verification issues
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

class SimpleKafkaTester:
    def __init__(self):
        """Initialize simple Kafka tester"""
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_unread = "zulip-unread-messages"
        self.kafka_topic_summaries = "zulip-summaries"
        self.service_url = "http://localhost:8080"
        
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
    
    def run_simple_test(self):
        """Run simple Kafka webhook test"""
        logger.info("Starting simple Kafka webhook test...")
        print("\n" + "="*70)
        print("SIMPLE KAFKA WEBHOOK TEST")
        print("="*70)
        
        # Test 1: Kafka connection
        print("\n1. Testing Kafka connection...")
        if not self.test_kafka_connection():
            print("   FAILED: Kafka is not accessible")
            return False
        print("   PASSED: Kafka is accessible")
        
        # Test 2: Service health
        print("\n2. Testing webhook service health...")
        if not self.test_service_health():
            print("   FAILED: Webhook service is not running")
            return False
        print("   PASSED: Webhook service is running")
        
        # Test 3: Send test data to Kafka
        print("\n3. Sending test unread messages to Kafka...")
        if not self.send_test_unread_to_kafka():
            print("   FAILED: Could not send test messages to Kafka")
            return False
        print("   PASSED: Test messages sent to Kafka")
        
        # Test 4: Check Kafka topics for messages
        print("\n4. Checking Kafka topics for messages...")
        time.sleep(3)  # Wait for processing
        
        unread_messages = self.check_kafka_messages(self.kafka_topic_unread, timeout=5)
        summary_messages = self.check_kafka_messages(self.kafka_topic_summaries, timeout=5)
        
        if unread_messages:
            print(f"   PASSED: Found {len(unread_messages)} messages in unread topic")
            for i, msg in enumerate(unread_messages[:3]):  # Show first 3 messages
                print(f"     Message {i+1}: {msg[:100]}...")
        else:
            print("   WARNING: No messages found in unread topic")
        
        if summary_messages:
            print(f"   PASSED: Found {len(summary_messages)} messages in summary topic")
            for i, msg in enumerate(summary_messages[:3]):  # Show first 3 messages
                print(f"     Summary {i+1}: {msg[:100]}...")
        else:
            print("   INFO: No summaries found (kafka_summary_processor may not be running)")
            print("   To see summaries, run: python kafka_summary_processor.py")
        
        print("\n" + "="*70)
        print("SIMPLE KAFKA WEBHOOK TEST COMPLETED!")
        print("="*70)
        
        print("\nNext steps to run the complete Kafka system:")
        print("1. python kafka_summary_processor.py (in new terminal)")
        print("2. python outgoing_webhook.py (in new terminal)")
        print("3. python incoming_webhook.py (in new terminal)")
        print("4. Send messages to Zulip streams monitored by the webhooks")
        print("="*70)
        
        return True

def main():
    """Main function to run simple Kafka tests"""
    tester = SimpleKafkaTester()
    
    try:
        success = tester.run_simple_test()
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
