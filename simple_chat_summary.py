#!/usr/bin/env python3
"""
Simple Chat Summary Processor
Version simplificada para diagnosticar problemas
"""

import json
import logging
import time
from datetime import datetime
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleChatSummaryProcessor:
    def __init__(self):
        """Initialize the simple chat summary processor"""
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_summaries = "zulip-summaries"
        self.summary_interval = 10  # 10 segundos para pruebas
        
        # Initialize Kafka producer
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            logger.info("Kafka producer initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Kafka producer: {e}")
            self.producer = None
    
    def generate_demo_summary(self, stream: str, topic: str) -> str:
        """Generate a simple demo summary"""
        return f"Resumen demo para {stream}/{topic}: Sistema funcionando correctamente con publicación en Kafka. Timestamp: {datetime.now().strftime('%H:%M:%S')}"
    
    def publish_summary_to_kafka(self, stream: str, topic: str, summary: str) -> bool:
        """Publish summary to Kafka summary topic"""
        try:
            payload = {
                "message_type": "simple_summary",
                "timestamp": datetime.now().isoformat(),
                "stream": stream,
                "topic": topic,
                "summary": summary,
                "message_count": 1,
                "processed_at": datetime.now().isoformat(),
                "server_url": "https://localhost:443",
                "processing_mode": "simple_test"
            }
            
            if self.producer:
                try:
                    key = f"{stream}-{topic}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_summaries,
                        key=key,
                        value=payload
                    )
                    
                    # Wait for the message to be sent
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Summary published successfully!")
                    logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sending to Kafka: {e}")
                    return False
            else:
                logger.error("Kafka producer not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing summary to Kafka: {e}")
            return False
    
    def run_simple_processor(self):
        """Run simple processor in round-robin"""
        logger.info("Starting Simple Chat Summary Processor...")
        logger.info(f"Processing one channel every {self.summary_interval} seconds")
        
        # Demo streams to process
        demo_streams = [
            {"stream": "general", "topic": "chat"},
            {"stream": "desarrollo", "topic": "proyecto"},
            {"stream": "equipo", "topic": "actualizaciones"},
            {"stream": "comercio", "topic": "ventas"}
        ]
        
        logger.info(f"Monitoring {len(demo_streams)} stream/topic combinations")
        
        current_channel_index = 0
        cycle_count = 0
        max_cycles = 8  # 8 ciclos para prueba
        
        while cycle_count < max_cycles:
            try:
                current_time = datetime.now()
                stream_data = demo_streams[current_channel_index]
                stream = stream_data["stream"]
                topic = stream_data["topic"]
                
                logger.info(f"=== Cycle {cycle_count + 1}/{max_cycles} ===")
                logger.info(f"Processing channel {current_channel_index + 1}/{len(demo_streams)}: {stream}/{topic} at {current_time.strftime('%H:%M:%S')}")
                
                # Generate simple summary
                summary = self.generate_demo_summary(stream, topic)
                logger.info(f"Generated summary: {summary}")
                
                # Publish summary to Kafka
                success = self.publish_summary_to_kafka(stream, topic, summary)
                
                if success:
                    logger.info(f"Successfully processed and published summary for {stream}/{topic}")
                else:
                    logger.error(f"Failed to publish summary for {stream}/{topic}")
                
                # Move to next channel
                current_channel_index = (current_channel_index + 1) % len(demo_streams)
                cycle_count += 1
                
                if cycle_count < max_cycles:
                    # Wait for the next cycle
                    logger.info(f"Waiting {self.summary_interval} seconds for next channel...")
                    time.sleep(self.summary_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping simple chat summary processor...")
                break
            except Exception as e:
                logger.error(f"Error in summary cycle: {e}")
                time.sleep(5)  # Wait before retrying
        
        logger.info("Simple processor completed successfully!")

def main():
    """Main function to run the simple chat summary processor"""
    processor = SimpleChatSummaryProcessor()
    
    try:
        logger.info("Starting Simple Chat Summary Processor...")
        processor.run_simple_processor()
    except KeyboardInterrupt:
        logger.info("Simple Chat Summary Processor stopped by user")
    except Exception as e:
        logger.error(f"Simple Chat Summary Processor error: {e}")

if __name__ == "__main__":
    main()
