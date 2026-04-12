#!/usr/bin/env python3
"""
Setup Kafka Topics for Webhook System
Create topics for unread messages and summaries
"""

import subprocess
import logging
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class KafkaSetup:
    def __init__(self):
        """Initialize Kafka setup"""
        self.kafka_bootstrap_servers = "localhost:9092"
        self.topics = {
            "zulip-unread-messages": {
                "partitions": 3,
                "replication_factor": 1,
                "description": "Topic for unread messages from Zulip streams"
            },
            "zulip-summaries": {
                "partitions": 3,
                "replication_factor": 1,
                "description": "Topic for generated summaries"
            }
        }
    
    def check_kafka_connection(self) -> bool:
        """Check if Kafka is running and accessible"""
        try:
            # Try to list existing topics
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--list"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info("Kafka is accessible")
                return True
            else:
                logger.error(f"Kafka connection failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Kafka connection timeout")
            return False
        except Exception as e:
            logger.error(f"Error checking Kafka connection: {e}")
            return False
    
    def list_existing_topics(self) -> list:
        """List existing Kafka topics"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--list"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
                logger.info(f"Existing topics: {topics}")
                return topics
            else:
                logger.error(f"Error listing topics: {result.stderr}")
                return []
                
        except Exception as e:
            logger.error(f"Error listing topics: {e}")
            return []
    
    def create_topic(self, topic_name: str, partitions: int, replication_factor: int) -> bool:
        """Create a Kafka topic"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--create", "--topic", topic_name,
                "--partitions", str(partitions),
                "--replication-factor", str(replication_factor)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Topic '{topic_name}' created successfully")
                return True
            elif "already exists" in result.stderr.lower():
                logger.info(f"Topic '{topic_name}' already exists")
                return True
            else:
                logger.error(f"Error creating topic '{topic_name}': {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating topic '{topic_name}': {e}")
            return False
    
    def describe_topic(self, topic_name: str) -> dict:
        """Get details about a Kafka topic"""
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--describe", "--topic", topic_name
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse the output to get topic details
                lines = result.stdout.strip().split('\n')
                details = {}
                for line in lines:
                    if topic_name in line:
                        parts = line.split('\t')
                        for part in parts:
                            if ':' in part:
                                key, value = part.split(':', 1)
                                details[key.strip()] = value.strip()
                return details
            else:
                logger.error(f"Error describing topic '{topic_name}': {result.stderr}")
                return {}
                
        except Exception as e:
            logger.error(f"Error describing topic '{topic_name}': {e}")
            return {}
    
    def setup_all_topics(self) -> bool:
        """Setup all required Kafka topics"""
        logger.info("Setting up Kafka topics...")
        
        # Check Kafka connection
        if not self.check_kafka_connection():
            logger.error("Cannot connect to Kafka. Please ensure Kafka is running.")
            return False
        
        # List existing topics
        existing_topics = self.list_existing_topics()
        
        # Create topics
        success = True
        for topic_name, config in self.topics.items():
            logger.info(f"Processing topic: {topic_name}")
            
            if topic_name in existing_topics:
                logger.info(f"Topic '{topic_name}' already exists")
                # Describe the topic to verify configuration
                details = self.describe_topic(topic_name)
                logger.info(f"Topic details: {details}")
            else:
                created = self.create_topic(
                    topic_name,
                    config["partitions"],
                    config["replication_factor"]
                )
                if not created:
                    success = False
        
        if success:
            logger.info("All Kafka topics setup completed successfully!")
            return True
        else:
            logger.error("Some topics failed to setup")
            return False
    
    def test_topic_access(self, topic_name: str) -> bool:
        """Test if we can produce/consume from a topic"""
        try:
            # Test producing a message
            test_message = json.dumps({
                "test": True,
                "timestamp": datetime.now().isoformat(),
                "topic": topic_name
            })
            
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "bash", "-c", f"echo '{test_message}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {topic_name}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logger.info(f"Successfully produced test message to '{topic_name}'")
                return True
            else:
                logger.error(f"Error producing to '{topic_name}': {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing topic access: {e}")
            return False

def main():
    """Main function to setup Kafka topics"""
    setup = KafkaSetup()
    
    try:
        print("="*60)
        print("KAFKA TOPICS SETUP")
        print("="*60)
        
        success = setup.setup_all_topics()
        
        if success:
            print("\n" + "="*60)
            print("KAFKA TOPICS SETUP COMPLETED!")
            print("="*60)
            print("\nTopics created:")
            for topic_name, config in setup.topics.items():
                print(f"- {topic_name}: {config['description']}")
            
            print("\nNext steps:")
            print("1. Update webhook scripts to use Kafka")
            print("2. Start Kafka consumers/producers")
            print("3. Test the complete flow")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("KAFKA TOPICS SETUP FAILED!")
            print("Please check the logs above for details")
            print("="*60)
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup error: {e}")

if __name__ == "__main__":
    main()
