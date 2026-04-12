#!/usr/bin/env python3
"""
Kafka Consumer for Message Summaries
Processes messages from Kafka and generates summaries using Gemini API
"""

import json
import time
import os
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any
from kafka import KafkaConsumer
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SummaryConsumer:
    """Consumer that processes Kafka messages and generates summaries using Gemini"""
    
    def __init__(self, kafka_config: Dict[str, Any]):
        self.kafka_config = kafka_config
        self.running = False
        
        # Initialize Gemini API
        gemini_api_key = os.getenv('gemikey')
        if not gemini_api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        genai.configure(api_key=gemini_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Initialize Kafka Consumer
        self.consumer = KafkaConsumer(
            'summary_triggers',
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            group_id='summary_processor_group',
            auto_offset_reset='latest'
        )
        
        # Local Ollama for small tasks
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.use_ollama = os.getenv('USE_OLLAMA', 'true').lower() == 'true'
        
        # Summary tracking
        self.recent_summaries = {}  # Cache to avoid duplicate summaries
        self.summary_producer = KafkaProducer(
            bootstrap_servers=kafka_config['bootstrap_servers'],
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8'),
            key_serializer=lambda k: k.encode('utf-8') if k else None
        )
        
        print("Summary Consumer initialized with Gemini API")
    
    def start_processing(self):
        """Start processing summary triggers"""
        self.running = True
        print("Starting summary processing...")
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self._process_summary_triggers)
        self.processing_thread.daemon = True
        self.processing_thread.start()
        
        print("Summary processing started")
    
    def stop_processing(self):
        """Stop processing"""
        self.running = False
        if hasattr(self, 'processing_thread'):
            self.processing_thread.join(timeout=5)
        print("Stopped summary processing")
    
    def _process_summary_triggers(self):
        """Process summary triggers from Kafka"""
        try:
            while self.running:
                # Poll for messages
                message_pack = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, messages in message_pack.items():
                    for message in messages:
                        try:
                            self._handle_summary_trigger(message.key, message.value)
                        except Exception as e:
                            print(f"Error processing summary trigger: {e}")
                
                time.sleep(0.1)  # Small delay to prevent busy waiting
                
        except Exception as e:
            print(f"Error in summary trigger processing: {e}")
    
    def _handle_summary_trigger(self, stream_topic: str, trigger_data: Dict[str, Any]):
        """Handle a single summary trigger"""
        try:
            print(f"Processing summary trigger for {stream_topic}: {trigger_data['trigger_type']}")
            
            # Check if we recently processed a summary for this stream
            if self._should_skip_summary(stream_topic, trigger_data):
                print(f"Skipping summary for {stream_topic} - recently processed")
                return
            
            # Generate summary
            summary = self._generate_summary(trigger_data)
            
            if summary:
                # Send summary to results topic
                summary_result = {
                    'stream_topic': stream_topic,
                    'trigger_type': trigger_data['trigger_type'],
                    'trigger_timestamp': trigger_data['trigger_timestamp'],
                    'summary_timestamp': datetime.now().isoformat(),
                    'message_count': trigger_data['message_count'],
                    'summary': summary,
                    'summary_type': 'gemini' if len(trigger_data['messages']) > 5 else 'local'
                }
                
                self.summary_producer.send(
                    'summary_results',
                    key=stream_topic,
                    value=summary_result
                )
                
                # Update cache
                self.recent_summaries[stream_topic] = {
                    'timestamp': datetime.now(),
                    'message_count': trigger_data['message_count']
                }
                
                print(f"Generated summary for {stream_topic}: {len(summary)} characters")
            
        except Exception as e:
            print(f"Error handling summary trigger for {stream_topic}: {e}")
    
    def _should_skip_summary(self, stream_topic: str, trigger_data: Dict[str, Any]) -> bool:
        """Check if summary should be skipped to avoid duplicates"""
        if stream_topic not in self.recent_summaries:
            return False
        
        last_summary = self.recent_summaries[stream_topic]
        time_diff = datetime.now() - last_summary['timestamp']
        
        # Skip if summary was generated less than 2 minutes ago
        if time_diff.total_seconds() < 120:
            return True
        
        # Skip if message count difference is less than 5
        message_diff = abs(trigger_data['message_count'] - last_summary['message_count'])
        if message_diff < 5:
            return True
        
        return False
    
    def _generate_summary(self, trigger_data: Dict[str, Any]) -> str:
        """Generate summary using Gemini API or local model"""
        messages = trigger_data['messages']
        stream_topic = trigger_data['stream_topic']
        
        if not messages:
            return ""
        
        # Choose processing method based on message count
        if len(messages) > 5:
            return self._generate_gemini_summary(messages, stream_topic)
        else:
            return self._generate_local_summary(messages, stream_topic)
    
    def _generate_gemini_summary(self, messages: List[Dict[str, Any]], stream_topic: str) -> str:
        """Generate summary using Gemini API"""
        try:
            # Build context from messages
            context = self._build_message_context(messages)
            
            # Create prompt for Gemini
            prompt = f"""
            Analiza los siguientes mensajes del chat y genera un resumen conciso y útil:

            Canal: {stream_topic}
            Total de mensajes: {len(messages)}
            Periodo: {self._format_time_range(messages)}

            Mensajes:
            {context}

            Genera un resumen que incluya:
            1. Temas principales discutidos
            2. Decisiones importantes tomadas
            3. Acciones requeridas o próximos pasos
            4. Menciones importantes a usuarios
            5. Puntos clave o información relevante

            Formato de respuesta:
            **Resumen de {stream_topic}**
            **Mensajes:** {len(messages)} | **Período:** {self._format_time_range(messages)}

            **Temas principales:**
            - [Lista los temas principales]

            **Decisiones tomadas:**
            - [Lista las decisiones importantes]

            **Acciones requeridas:**
            - [Lista las acciones o tareas pendientes]

            **Menciones importantes:**
            - [Lista las menciones a usuarios]

            **Puntos clave:**
            - [Lista la información más relevante]

            Mantén el resumen conciso pero completo, máximo 300 palabras.
            """
            
            # Generate response with Gemini
            response = self.gemini_model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                print("Gemini API returned empty response")
                return self._generate_local_summary(messages, stream_topic)
                
        except Exception as e:
            print(f"Error generating Gemini summary: {e}")
            return self._generate_local_summary(messages, stream_topic)
    
    def _generate_local_summary(self, messages: List[Dict[str, Any]], stream_topic: str) -> str:
        """Generate summary using local Ollama model"""
        try:
            if not self.use_ollama:
                return self._generate_simple_summary(messages, stream_topic)
            
            # Build simplified prompt for local model
            context = self._build_message_context(messages)
            
            prompt = f"""
            Resume estos mensajes de forma breve:

            Canal: {stream_topic}
            Mensajes: {len(messages)}

            {context}

            Genera un resumen simple de máximo 150 palabras.
            """
            
            payload = {
                "model": "gemma3:1b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', '').strip()
            else:
                print(f"Ollama error: {response.status_code}")
                return self._generate_simple_summary(messages, stream_topic)
                
        except Exception as e:
            print(f"Error generating local summary: {e}")
            return self._generate_simple_summary(messages, stream_topic)
    
    def _generate_simple_summary(self, messages: List[Dict[str, Any]], stream_topic: str) -> str:
        """Generate a simple summary without AI"""
        try:
            # Extract key information
            senders = set()
            topics = set()
            message_count = len(messages)
            
            for msg in messages:
                senders.add(msg.get('sender_full_name', 'Unknown'))
                # Simple topic extraction from content
                content = msg.get('content', '').lower()
                if any(word in content for word in ['decisión', 'acuerdo', 'acordado']):
                    topics.add('decisiones')
                if any(word in content for word in ['tarea', 'hacer', 'realizar']):
                    topics.add('tareas')
                if any(word in content for word in ['problema', 'error', 'issue']):
                    topics.add('problemas')
            
            # Create simple summary
            summary = f"""**Resumen de {stream_topic}**
**Mensajes:** {message_count}
**Participantes:** {', '.join(list(senders)[:3])}{'...' if len(senders) > 3 else ''}
**Temas:** {', '.join(list(topics)) if topics else 'Conversación general'}

Resumen generado automáticamente de {message_count} mensajes."""
            
            return summary
            
        except Exception as e:
            print(f"Error generating simple summary: {e}")
            return f"Resumen de {stream_topic}: {message_count} mensajes procesados"
    
    def _build_message_context(self, messages: List[Dict[str, Any]]) -> str:
        """Build context string from messages"""
        context_lines = []
        
        for i, msg in enumerate(messages[-10:], 1):  # Last 10 messages
            sender = msg.get('sender_full_name', 'Unknown')
            content = msg.get('content', '')[:200]  # Truncate long messages
            timestamp = datetime.fromtimestamp(msg.get('timestamp', 0)).strftime('%H:%M')
            
            context_lines.append(f"{i}. [{timestamp}] {sender}: {content}")
        
        return '\n'.join(context_lines)
    
    def _format_time_range(self, messages: List[Dict[str, Any]]) -> str:
        """Format time range for messages"""
        if not messages:
            return "N/A"
        
        timestamps = [msg.get('timestamp', 0) for msg in messages]
        min_time = datetime.fromtimestamp(min(timestamps))
        max_time = datetime.fromtimestamp(max(timestamps))
        
        if min_time.date() == max_time.date():
            return f"{min_time.strftime('%H:%M')} - {max_time.strftime('%H:%M')}"
        else:
            return f"{min_time.strftime('%d/%m %H:%M')} - {max_time.strftime('%d/%m %H:%M')}"

def main():
    """Main function to run the summary consumer"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Kafka Consumer for Message Summaries')
    parser.add_argument('--kafka-servers', default='localhost:9092', help='Kafka bootstrap servers')
    
    args = parser.parse_args()
    
    # Configuration
    kafka_config = {
        'bootstrap_servers': args.kafka_servers.split(',')
    }
    
    # Create and start consumer
    try:
        consumer = SummaryConsumer(kafka_config)
        consumer.start_processing()
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("Shutting down...")
        consumer.stop_processing()
    except Exception as e:
        print(f"Error: {e}")
        if 'consumer' in locals():
            consumer.stop_processing()

if __name__ == '__main__':
    main()
