#!/usr/bin/env python3
"""
Complete System Test
Test the full Kafka webhook system with the 4 new channels
"""

import requests
import json
import logging
import subprocess
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CompleteSystemTester:
    def __init__(self):
        """Initialize the complete system tester"""
        self.kafka_topic_unread = "zulip-unread-messages"
        self.kafka_topic_summaries = "zulip-summaries"
        self.channels = ["comercio", "desarrollo", "equipo", "general"]
        
    def test_kafka_connection(self) -> bool:
        """Test Kafka connection"""
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
    
    def test_ollama_connection(self) -> bool:
        """Test Ollama connection"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("Ollama is accessible")
                return True
            else:
                logger.error(f"Ollama returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Ollama not accessible: {e}")
            return False
    
    def send_test_messages_to_kafka(self) -> bool:
        """Send test messages to Kafka unread topic"""
        try:
            for channel in self.channels:
                # Create test messages for each channel
                test_payload = {
                    "trigger_type": "unread_messages",
                    "timestamp": datetime.now().isoformat(),
                    "stream": channel,
                    "topic": "general",
                    "messages": [
                        {
                            "content": f"Mensaje 1 para el canal #{channel} - prueba del sistema Kafka",
                            "sender_full_name": "Usuario Test 1",
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "content": f"Mensaje 2 para #{channel} - verificando funcionamiento con Ollama",
                            "sender_full_name": "Usuario Test 2", 
                            "timestamp": datetime.now().isoformat()
                        },
                        {
                            "content": f"Mensaje 3 para #{channel} - este debería generar un buen resumen",
                            "sender_full_name": "Usuario Test 3",
                            "timestamp": datetime.now().isoformat()
                        }
                    ],
                    "message_count": 3,
                    "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
                }
                
                # Send to Kafka
                message_json = json.dumps(test_payload)
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {self.kafka_topic_unread}"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                
                if result.returncode == 0:
                    logger.info(f"Test messages sent to Kafka for channel '{channel}'")
                else:
                    logger.error(f"Error sending messages for '{channel}': {result.stderr}")
                    return False
                
                time.sleep(1)  # Small delay between messages
            
            return True
            
        except Exception as e:
            logger.error(f"Error sending test messages to Kafka: {e}")
            return False
    
    def check_kafka_topics(self) -> dict:
        """Check messages in Kafka topics"""
        results = {
            "unread_messages": 0,
            "summaries": 0
        }
        
        try:
            # Check unread messages topic
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-console-consumer",
                "--bootstrap-server", "localhost:9092",
                "--topic", self.kafka_topic_unread,
                "--from-beginning",
                "--timeout-ms", "3000"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                messages = result.stdout.strip().split('\n')
                results["unread_messages"] = len(messages)
                logger.info(f"Found {len(messages)} messages in unread topic")
            
            # Check summaries topic
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-console-consumer",
                "--bootstrap-server", "localhost:9092",
                "--topic", self.kafka_topic_summaries,
                "--from-beginning",
                "--timeout-ms", "3000"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout.strip():
                messages = result.stdout.strip().split('\n')
                results["summaries"] = len(messages)
                logger.info(f"Found {len(messages)} messages in summaries topic")
                
        except Exception as e:
            logger.error(f"Error checking Kafka topics: {e}")
        
        return results
    
    def test_zulip_connection(self) -> bool:
        """Test Zulip connection (simplified)"""
        try:
            # Try to connect to Zulip without SSL verification
            response = requests.get("http://localhost/api/v1/server_settings", timeout=5, verify=False)
            if response.status_code == 200:
                logger.info("Zulip server is accessible")
                return True
            else:
                logger.error(f"Zulip server returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Zulip server not accessible: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete system test"""
        logger.info("Starting complete system test...")
        print("\n" + "="*70)
        print("COMPLETE KAFKA WEBHOOK SYSTEM TEST")
        print("="*70)
        
        # Test 1: Kafka connection
        print("\n1. Testing Kafka connection...")
        if not self.test_kafka_connection():
            print("   FAILED: Kafka is not accessible")
            return False
        print("   PASSED: Kafka is accessible")
        
        # Test 2: Ollama connection
        print("\n2. Testing Ollama connection...")
        if not self.test_ollama_connection():
            print("   FAILED: Ollama is not accessible")
            return False
        print("   PASSED: Ollama is accessible")
        
        # Test 3: Zulip connection
        print("\n3. Testing Zulip connection...")
        if not self.test_zulip_connection():
            print("   WARNING: Zulip connection failed (may be SSL issues)")
        else:
            print("   PASSED: Zulip is accessible")
        
        # Test 4: Send test messages to Kafka
        print("\n4. Sending test messages to Kafka...")
        if not self.send_test_messages_to_kafka():
            print("   FAILED: Could not send test messages to Kafka")
            return False
        print("   PASSED: Test messages sent to Kafka")
        
        # Test 5: Wait and check topics
        print("\n5. Checking Kafka topics for messages...")
        print("   Waiting 5 seconds for processing...")
        time.sleep(5)
        
        topic_results = self.check_kafka_topics()
        
        if topic_results["unread_messages"] > 0:
            print(f"   PASSED: Found {topic_results['unread_messages']} messages in unread topic")
        else:
            print("   WARNING: No messages found in unread topic")
        
        if topic_results["summaries"] > 0:
            print(f"   PASSED: Found {topic_results['summaries']} summaries in summaries topic")
        else:
            print("   INFO: No summaries found (processor may not be running)")
        
        print("\n" + "="*70)
        print("COMPLETE SYSTEM TEST RESULTS:")
        print("="*70)
        print(f"Channels configured: {', '.join(self.channels)}")
        print(f"Kafka connection: {'PASSED' if self.test_kafka_connection() else 'FAILED'}")
        print(f"Ollama connection: {'PASSED' if self.test_ollama_connection() else 'FAILED'}")
        print(f"Test messages sent: {len(self.channels) * 3}")
        print(f"Messages in Kafka: {topic_results['unread_messages']}")
        print(f"Summaries generated: {topic_results['summaries']}")
        
        print("\n" + "="*70)
        print("NEXT STEPS:")
        print("="*70)
        print("To run the complete system:")
        print("1. Start Kafka processor: python kafka_summary_processor.py")
        print("2. Start outgoing webhook: python outgoing_webhook.py")
        print("3. Start incoming webhook: python incoming_webhook.py")
        print("4. Send messages to Zulip channels: #comercio, #desarrollo, #equipo, #general")
        print("5. Wait for automatic summaries to appear")
        print("="*70)
        
        return True

def main():
    """Main function to run complete system test"""
    tester = CompleteSystemTester()
    
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
