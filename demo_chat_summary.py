#!/usr/bin/env python3
"""
Demo Chat Summary Processor
Generates demo summaries and publishes to Kafka every minute
"""

import json
import logging
import time
from datetime import datetime
from kafka import KafkaProducer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DemoChatSummaryProcessor:
    def __init__(self):
        """Initialize the demo chat summary processor"""
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_summaries = "zulip-summaries"
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "gemma2:2b"
        self.summary_interval = 60  # 1 minute
        
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
    
    def generate_demo_messages(self, stream: str, topic: str) -> list:
        """Generate demo messages for testing"""
        demo_messages = [
            {
                "id": 1001,
                "content": "Hola equipo, ¿cómo está el progreso del proyecto Kafka?",
                "sender_full_name": "Juan Pérez",
                "timestamp": datetime.now().timestamp() - 300,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/1001"
            },
            {
                "id": 1002,
                "content": "Va bien, ya terminamos la implementación de los enlaces directos en mensajes",
                "sender_full_name": "María García",
                "timestamp": datetime.now().timestamp() - 240,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/1002"
            },
            {
                "id": 1003,
                "content": "Excelente, ya podemos generar resúmenes cada 1 minuto como solicitó el usuario",
                "sender_full_name": "Carlos López",
                "timestamp": datetime.now().timestamp() - 180,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/1003"
            },
            {
                "id": 1004,
                "content": "Los resúmenes se publican en el topic zulip-summaries de Kafka",
                "sender_full_name": "Ana Martínez",
                "timestamp": datetime.now().timestamp() - 120,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/1004"
            },
            {
                "id": 1005,
                "content": "Perfecto, el sistema está funcionando con enlaces directos incluidos",
                "sender_full_name": "Juan Pérez",
                "timestamp": datetime.now().timestamp() - 60,
                "direct_link": f"https://localhost:443/#narrow/stream/{stream}/topic/{topic}/near/1005"
            }
        ]
        
        return demo_messages
    
    def generate_summary_with_ollama(self, messages: list, stream: str, topic: str) -> str:
        """Generate summary of messages using Ollama"""
        try:
            # Extract message content with links
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", 0)
                direct_link = msg.get("direct_link", "")
                
                # Format message with timestamp and link
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                if direct_link:
                    formatted_msg = f"[{time_str}] **{sender}**: {content} [Ver mensaje]({direct_link})"
                else:
                    formatted_msg = f"[{time_str}] **{sender}**: {content}"
                
                message_texts.append(formatted_msg)
            
            # Create prompt for Ollama
            all_messages = "\n".join(message_texts)
            prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del stream "{stream}" en el topic "{topic}".

Mensajes recientes:
{all_messages}

Instrucciones:
1. Identifica los puntos principales y temas discutidos
2. Menciona decisiones importantes si las hay
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 150 palabras)
6. Incluye enlaces a los mensajes originales cuando sea relevante

Resumen:
"""
            
            # Call Ollama API
            ollama_payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 400
                }
            }
            
            import requests
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary = result.get("response", "").strip()
                logger.info(f"Generated summary for {stream}/{topic}")
                return summary
            else:
                logger.error(f"Error calling Ollama: {response.status_code}")
                return f"Error generando resumen para {stream}/{topic}"
                
        except Exception as e:
            logger.error(f"Error generating summary with Ollama: {e}")
            return f"No se pudo generar el resumen debido a un error: {str(e)}"
    
    def publish_summary_to_kafka(self, stream: str, topic: str, summary: str, messages: list) -> bool:
        """Publish summary to Kafka summary topic"""
        try:
            # Extract message links for the summary
            message_links = []
            for msg in messages:
                message_links.append({
                    "id": msg.get("id"),
                    "sender": msg.get("sender_full_name", "Unknown"),
                    "content_preview": msg.get("content", "")[:50] + "...",
                    "direct_link": msg.get("direct_link", ""),
                    "timestamp": msg.get("timestamp", 0)
                })
            
            payload = {
                "message_type": "chat_summary",
                "timestamp": datetime.now().isoformat(),
                "stream": stream,
                "topic": topic,
                "summary": summary,
                "message_count": len(messages),
                "message_links": message_links,
                "summary_period_minutes": 5,
                "processed_at": datetime.now().isoformat(),
                "server_url": "https://localhost:443"
            }
            
            # Send to Kafka using KafkaProducer
            if self.producer:
                try:
                    key = f"{stream}-{topic}-{datetime.now().strftime('%Y%m%d%H%M')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_summaries,
                        key=key,
                        value=payload
                    )
                    
                    # Wait for the message to be sent
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Summary published successfully to Kafka topic '{self.kafka_topic_summaries}'")
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
    
    def run_demo(self):
        """Run demo summary processor"""
        logger.info("Starting Demo Chat Summary Processor...")
        logger.info(f"Generating demo summaries every {self.summary_interval} seconds")
        
        # Demo streams to process
        demo_streams = [
            {"stream": "general", "topic": "chat"},
            {"stream": "desarrollo", "topic": "proyecto"},
            {"stream": "equipo", "topic": "actualizaciones"}
        ]
        
        cycle_count = 0
        max_cycles = 5  # Run for 5 cycles (5 minutes)
        
        while cycle_count < max_cycles:
            try:
                current_time = datetime.now()
                logger.info(f"Running demo summary cycle #{cycle_count + 1} at {current_time.strftime('%H:%M:%S')}")
                
                for stream_data in demo_streams:
                    stream = stream_data["stream"]
                    topic = stream_data["topic"]
                    
                    logger.info(f"Processing {stream}/{topic}")
                    
                    # Generate demo messages
                    messages = self.generate_demo_messages(stream, topic)
                    
                    # Add some variation to messages
                    for i, msg in enumerate(messages):
                        msg["id"] += cycle_count * 100
                        msg["timestamp"] = current_time.timestamp() - (5 - i) * 60
                    
                    # Generate summary
                    logger.info(f"Generating summary for {stream}/{topic} with {len(messages)} messages")
                    summary = self.generate_summary_with_ollama(messages, stream, topic)
                    
                    # Publish summary to Kafka
                    success = self.publish_summary_to_kafka(stream, topic, summary, messages)
                    
                    if success:
                        logger.info(f"Successfully processed and published summary for {stream}/{topic}")
                        print(f"\n=== SUMMARY FOR {stream}/{topic} ===")
                        print(summary)
                        print("=" * 50)
                    else:
                        logger.error(f"Failed to publish summary for {stream}/{topic}")
                
                cycle_count += 1
                
                if cycle_count < max_cycles:
                    # Wait for the next cycle
                    logger.info(f"Waiting {self.summary_interval} seconds for next summary cycle...")
                    time.sleep(self.summary_interval)
                
            except KeyboardInterrupt:
                logger.info("Stopping demo chat summary processor...")
                break
            except Exception as e:
                logger.error(f"Error in summary cycle: {e}")
                time.sleep(30)  # Wait before retrying
        
        logger.info("Demo completed successfully!")

def main():
    """Main function to run the demo chat summary processor"""
    processor = DemoChatSummaryProcessor()
    
    try:
        logger.info("Starting Demo Chat Summary Processor...")
        processor.run_demo()
    except KeyboardInterrupt:
        logger.info("Demo Chat Summary Processor stopped by user")
    except Exception as e:
        logger.error(f"Demo Chat Summary Processor error: {e}")

if __name__ == "__main__":
    main()
