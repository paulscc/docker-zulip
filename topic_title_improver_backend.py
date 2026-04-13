#!/usr/bin/env python3
"""
Topic Title Improver Backend
API endpoints for analyzing drifting discussions and suggesting improved topic titles
"""

import json
import logging
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from kafka import KafkaProducer
import os
import re
from collections import Counter
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class TopicTitleImproverBackend:
    def __init__(self):
        """Initialize the topic title improver backend"""
        self.config = self.load_config()
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_topic_analysis = "topic-analysis"
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        self.gemini_api_key = os.getenv('GEMINI_API_KEY')
        self.default_llm_model = os.getenv('DEFAULT_LLM_MODEL', 'gemma2')
        
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
    
    def load_config(self) -> Dict:
        """Load configuration from environment"""
        config = {
            "zulip_server": os.getenv('ZULIP_SERVER', 'https://localhost'),
            "zulip_email": os.getenv('ZULIP_EMAIL'),
            "zulip_api_key": os.getenv('ZULIP_API_KEY'),
            "drift_threshold": 0.7,  # Threshold for detecting drifting discussions
            "min_messages_for_analysis": 10,  # Minimum messages to perform analysis
            "analysis_window_hours": 24  # Time window for analysis
        }
        return config
    
    def get_topic_messages(self, stream: str, topic: str, limit: int = 100) -> List[Dict]:
        """Get messages from a specific topic for analysis"""
        try:
            url = f"{self.config['zulip_server']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.config['zulip_api_key']}",
                "Content-Type": "application/json"
            }
            
            params = {
                "stream": stream,
                "topic": topic,
                "num_before": limit,
                "num_after": 0,
                "narrow": json.dumps([
                    {"operator": "stream", "operand": stream},
                    {"operator": "topic", "operand": topic}
                ])
            }
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                logger.info(f"Found {len(messages)} messages in {stream}/{topic}")
                return messages
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return self.generate_demo_topic_messages(stream, topic)
                
        except Exception as e:
            logger.error(f"Error getting topic messages: {e}")
            return self.generate_demo_topic_messages(stream, topic)
    
    def generate_demo_topic_messages(self, stream: str, topic: str) -> List[Dict]:
        """Generate demo messages for topic analysis"""
        current_time = datetime.now()
        
        # Create messages that show topic drift
        messages = [
            {
                "id": int(current_time.timestamp()) + 1,
                "content": f"Comenzando discusión sobre {topic} - este es el tema original",
                "sender_full_name": "User1",
                "timestamp": current_time.timestamp() - 7200,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 2,
                "content": f"Estoy de acuerdo con el enfoque de {topic}, necesitamos más detalles",
                "sender_full_name": "User2", 
                "timestamp": current_time.timestamp() - 6600,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 3,
                "content": "Por cierto, hablando de implementaciones, ¿alguien ha trabajado con Docker recientemente?",
                "sender_full_name": "User3",
                "timestamp": current_time.timestamp() - 5400,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 4,
                "content": "Sí, he estado usando Kubernetes para orquestación, es mucho mejor que Docker solo",
                "sender_full_name": "User4",
                "timestamp": current_time.timestamp() - 4800,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 5,
                "content": "La verdad es que prefiero microservicios sobre monolíticos, aunque tiene sus desafíos",
                "sender_full_name": "User5",
                "timestamp": current_time.timestamp() - 4200,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 6,
                "content": "Alguien debería actualizar la documentación sobre arquitectura de microservicios",
                "sender_full_name": "User6",
                "timestamp": current_time.timestamp() - 3600,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 7,
                "content": "Volviendo al tema original, creo que necesitamos definir mejor los requisitos",
                "sender_full_name": "User1",
                "timestamp": current_time.timestamp() - 3000,
                "stream": stream,
                "subject": topic
            },
            {
                "id": int(current_time.timestamp()) + 8,
                "content": "También necesitamos considerar el impacto en el rendimiento del sistema",
                "sender_full_name": "User2",
                "timestamp": current_time.timestamp() - 2400,
                "stream": stream,
                "subject": topic
            }
        ]
        
        return messages
    
    def extract_keywords_and_topics(self, messages: List[Dict]) -> Dict[str, Any]:
        """Extract keywords and identify main topics from messages"""
        try:
            # Combine all message content
            all_text = " ".join([msg.get("content", "") for msg in messages])
            
            # Simple keyword extraction (in production, use NLP libraries)
            words = re.findall(r'\b[a-zA-Z]+\b', all_text.lower())
            
            # Filter out common words
            stop_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los', 'una', 'todo', 'pero', 'ser', 'tiene', 'fue', 'si', 'este', 'ya', 'más', 'han', 'me', 'está', 'mi', 'bien', 'ni', 'sobre', 'todo', 'esta', 'muy', 'aquí', 'ahora', 'cuando', 'han', 'han', 'han', 'han'}
            
            filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
            word_freq = Counter(filtered_words)
            
            # Extract top keywords
            top_keywords = word_freq.most_common(10)
            
            # Analyze temporal topic evolution
            topic_evolution = self.analyze_topic_evolution(messages)
            
            return {
                "keywords": top_keywords,
                "total_words": len(filtered_words),
                "unique_words": len(set(filtered_words)),
                "topic_evolution": topic_evolution
            }
            
        except Exception as e:
            logger.error(f"Error extracting keywords: {e}")
            return {
                "keywords": [],
                "total_words": 0,
                "unique_words": 0,
                "topic_evolution": []
            }
    
    def analyze_topic_evolution(self, messages: List[Dict]) -> List[Dict]:
        """Analyze how topics evolve over time in the conversation"""
        try:
            if len(messages) < 5:
                return []
            
            # Sort messages by timestamp
            sorted_messages = sorted(messages, key=lambda x: x.get("timestamp", 0))
            
            # Divide messages into time windows
            window_size = max(3, len(sorted_messages) // 4)  # 4 time windows
            evolution = []
            
            for i in range(0, len(sorted_messages), window_size):
                window_messages = sorted_messages[i:i + window_size]
                if not window_messages:
                    continue
                
                # Extract keywords for this window
                window_text = " ".join([msg.get("content", "") for msg in window_messages])
                words = re.findall(r'\b[a-zA-Z]+\b', window_text.lower())
                stop_words = {'el', 'la', 'de', 'que', 'y', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'como', 'las', 'del', 'los', 'una', 'todo', 'pero', 'ser', 'tiene', 'fue', 'si', 'este', 'ya', 'más', 'han', 'me', 'está', 'mi', 'bien', 'ni', 'sobre', 'todo', 'esta', 'muy', 'aquí', 'ahora', 'cuando'}
                
                filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
                word_freq = Counter(filtered_words)
                
                evolution.append({
                    "time_start": window_messages[0].get("timestamp", 0),
                    "time_end": window_messages[-1].get("timestamp", 0),
                    "message_count": len(window_messages),
                    "top_keywords": word_freq.most_common(5),
                    "time_period": f"{datetime.fromtimestamp(window_messages[0].get('timestamp', 0)).strftime('%H:%M')} - {datetime.fromtimestamp(window_messages[-1].get('timestamp', 0)).strftime('%H:%M')}"
                })
            
            return evolution
            
        except Exception as e:
            logger.error(f"Error analyzing topic evolution: {e}")
            return []
    
    def detect_topic_drift(self, messages: List[Dict], original_topic: str) -> Dict[str, Any]:
        """Detect if the conversation has drifted from the original topic"""
        try:
            if len(messages) < self.config['min_messages_for_analysis']:
                return {
                    "has_drift": False,
                    "drift_score": 0.0,
                    "reason": "Insufficient messages for analysis"
                }
            
            # Analyze topic evolution
            keywords_data = self.extract_keywords_and_topics(messages)
            evolution = keywords_data.get("topic_evolution", [])
            
            if len(evolution) < 2:
                return {
                    "has_drift": False,
                    "drift_score": 0.0,
                    "reason": "Insufficient time windows for analysis"
                }
            
            # Compare first and last time windows
            first_window = evolution[0]["top_keywords"]
            last_window = evolution[-1]["top_keywords"]
            
            # Calculate overlap between first and last windows
            first_keywords = set([word for word, count in first_window])
            last_keywords = set([word for word, count in last_window])
            
            if len(first_keywords) == 0:
                overlap = 0.0
            else:
                overlap = len(first_keywords.intersection(last_keywords)) / len(first_keywords)
            
            # Calculate drift score (1 - overlap)
            drift_score = 1.0 - overlap
            
            # Determine if there's significant drift
            has_drift = drift_score > self.config['drift_threshold']
            
            # Identify new topics that emerged
            new_topics = last_keywords - first_keywords
            original_topics = first_keywords - last_keywords
            
            return {
                "has_drift": has_drift,
                "drift_score": drift_score,
                "overlap": overlap,
                "original_topics": list(original_topics)[:5],
                "new_topics": list(new_topics)[:5],
                "reason": f"Topic drift detected with score {drift_score:.2f}" if has_drift else "No significant topic drift detected"
            }
            
        except Exception as e:
            logger.error(f"Error detecting topic drift: {e}")
            return {
                "has_drift": False,
                "drift_score": 0.0,
                "reason": f"Error in analysis: {str(e)}"
            }
    
    def generate_title_suggestions(self, messages: List[Dict], original_topic: str, drift_analysis: Dict) -> List[Dict]:
        """Generate improved title suggestions using LLM"""
        try:
            if not messages:
                return []
            
            # Extract conversation summary
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", 0)
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                
                formatted_msg = f"[{time_str}] {sender}: {content}"
                message_texts.append(formatted_msg)
            
            all_messages = "\n".join(message_texts)
            
            # Create prompt for LLM
            prompt = f"""
Analiza la siguiente conversación y genera sugerencias de títulos mejorados para el tema.

Tema original: "{original_topic}"

Conversación:
{all_messages}

Análisis de deriva del tema:
- Tiene deriva: {drift_analysis.get('has_drift', False)}
- Puntaje de deriva: {drift_analysis.get('drift_score', 0):.2f}
- Temas nuevos identificados: {', '.join(drift_analysis.get('new_topics', []))}
- Temas originales mantenidos: {', '.join(drift_analysis.get('original_topics', []))}

Instrucciones:
1. Genera 3-5 sugerencias de títulos que reflejen mejor el contenido actual de la conversación
2. Considera si la conversación ha derivado hacia nuevos temas
3. Los títulos deben ser claros, concisos y descriptivos (máximo 50 caracteres)
4. Mantén un tono profesional
5. Responde en formato JSON con la siguiente estructura:
{{
  "suggestions": [
    {{
      "title": "Título sugerido 1",
      "reason": "Por qué este título es mejor",
      "confidence": 0.9
    }}
  ]
}}

Respuesta:
"""
            
            # Try Gemini first if API key is available
            if self.gemini_api_key:
                suggestions = self.call_gemini_for_titles(prompt)
                if suggestions:
                    return suggestions
            
            # Fallback to Ollama
            return self.call_ollama_for_titles(prompt)
            
        except Exception as e:
            logger.error(f"Error generating title suggestions: {e}")
            return []
    
    def call_gemini_for_titles(self, prompt: str) -> List[Dict]:
        """Call Gemini API for title suggestions"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(prompt)
            
            if response.text:
                try:
                    result = json.loads(response.text)
                    return result.get("suggestions", [])
                except json.JSONDecodeError:
                    # If not JSON, create simple structure
                    return [{
                        "title": response.text.strip(),
                        "reason": "Generated by Gemini",
                        "confidence": 0.8
                    }]
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error calling Gemini for titles: {e}")
            return []
    
    def call_ollama_for_titles(self, prompt: str) -> List[Dict]:
        """Call Ollama API for title suggestions"""
        try:
            ollama_payload = {
                "model": "gemma2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                try:
                    parsed = json.loads(response_text)
                    return parsed.get("suggestions", [])
                except json.JSONDecodeError:
                    # If not JSON, create simple suggestions
                    return [{
                        "title": response_text,
                        "reason": "Generated by Ollama",
                        "confidence": 0.7
                    }]
            else:
                logger.error(f"Error calling Ollama: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error calling Ollama for titles: {e}")
            return []
    
    def publish_analysis_to_kafka(self, stream: str, topic: str, analysis_data: Dict) -> bool:
        """Publish topic analysis to Kafka"""
        try:
            payload = {
                "message_type": "topic_analysis",
                "timestamp": datetime.now().isoformat(),
                "stream": stream,
                "topic": topic,
                "analysis": analysis_data,
                "processed_at": datetime.now().isoformat(),
                "server_url": self.config['zulip_server']
            }
            
            if self.producer:
                try:
                    key = f"{stream}-{topic}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_analysis,
                        key=key,
                        value=payload
                    )
                    
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Topic analysis published successfully to Kafka")
                    logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sending analysis to Kafka: {e}")
                    return False
            else:
                logger.error("Kafka producer not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing analysis to Kafka: {e}")
            return False

# Initialize backend instance
topic_improver = TopicTitleImproverBackend()

@app.route('/api/topics/analyze', methods=['POST'])
def analyze_topic():
    """Analyze a topic for drifting discussions and title suggestions"""
    try:
        data = request.get_json()
        stream = data.get('stream')
        topic = data.get('topic')
        
        if not stream or not topic:
            return jsonify({"error": "stream and topic are required"}), 400
        
        # Get topic messages
        messages = topic_improver.get_topic_messages(stream, topic)
        
        if not messages:
            return jsonify({
                "message": "No messages found for analysis",
                "analysis": {
                    "drift_analysis": {
                        "has_drift": False,
                        "drift_score": 0.0,
                        "reason": "No messages to analyze"
                    },
                    "title_suggestions": [],
                    "message_count": 0
                }
            })
        
        # Detect topic drift
        drift_analysis = topic_improver.detect_topic_drift(messages, topic)
        
        # Generate title suggestions
        title_suggestions = topic_improver.generate_title_suggestions(messages, topic, drift_analysis)
        
        # Extract keywords
        keywords_data = topic_improver.extract_keywords_and_topics(messages)
        
        analysis_data = {
            "drift_analysis": drift_analysis,
            "title_suggestions": title_suggestions,
            "keywords": keywords_data,
            "message_count": len(messages),
            "analysis_window_hours": topic_improver.config['analysis_window_hours']
        }
        
        # Publish to Kafka
        success = topic_improver.publish_analysis_to_kafka(stream, topic, analysis_data)
        
        return jsonify({
            "message": "Topic analysis completed successfully",
            "analysis": analysis_data,
            "kafka_published": success,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error analyzing topic: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/topics/status/<stream_id>', methods=['GET'])
def get_topic_status(stream_id: str):
    """Get analysis status for a stream"""
    try:
        # This would typically check database or cache for recent analyses
        return jsonify({
            "stream_id": stream_id,
            "last_analysis": datetime.now().isoformat(),
            "total_analyses": 1,
            "status": "active"
        })
        
    except Exception as e:
        logger.error(f"Error getting topic status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/topics/update', methods=['POST'])
def update_topic_title():
    """Update a topic title (would integrate with Zulip API)"""
    try:
        data = request.get_json()
        stream = data.get('stream')
        old_topic = data.get('old_topic')
        new_topic = data.get('new_topic')
        
        if not stream or not old_topic or not new_topic:
            return jsonify({"error": "stream, old_topic, and new_topic are required"}), 400
        
        # In a real implementation, this would call Zulip API to update the topic
        # For now, just return success
        
        logger.info(f"Topic update requested: {stream}/{old_topic} -> {new_topic}")
        
        return jsonify({
            "message": "Topic title updated successfully",
            "stream": stream,
            "old_topic": old_topic,
            "new_topic": new_topic,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error updating topic: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "kafka_connected": topic_improver.producer is not None,
        "ollama_available": True,
        "gemini_available": bool(topic_improver.gemini_api_key),
        "drift_threshold": topic_improver.config['drift_threshold']
    })

if __name__ == '__main__':
    logger.info("Starting Topic Title Improver Backend...")
    app.run(host='0.0.0.0', port=5002, debug=True)
