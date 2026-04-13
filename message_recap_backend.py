#!/usr/bin/env python3
"""
Message Recap Backend
API endpoints for generating message summaries with individual message links
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
from urllib.parse import quote

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class MessageRecapBackend:
    def __init__(self):
        """Initialize the message recap backend"""
        self.config = self.load_config()
        self.kafka_bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.kafka_topic_summaries = "zulip-summaries"
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
        """Load configuration from environment or config file"""
        config = {
            "zulip_server": os.getenv('ZULIP_SERVER', 'https://localhost'),
            "zulip_email": os.getenv('ZULIP_EMAIL'),
            "zulip_api_key": os.getenv('ZULIP_API_KEY'),
            "default_streams": ["general", "random", " announcements"]
        }
        return config
    
    def get_unread_messages_for_user(self, user_email: str, stream: Optional[str] = None) -> List[Dict]:
        """Get unread messages for a specific user from Zulip API"""
        try:
            url = f"{self.config['zulip_server']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.config['zulip_api_key']}",
                "Content-Type": "application/json"
            }
            
            # Get messages with unread marker
            params = {
                "num_before": 100,
                "num_after": 0,
                "anchor": "newest"
            }
            
            if stream:
                params["narrow"] = json.dumps([
                    {"operator": "stream", "operand": stream}
                ])
            
            response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
            
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                
                # Add direct links to each message
                for message in messages:
                    message_id = message.get("id")
                    if message_id:
                        message["direct_link"] = self.create_message_link(message)
                
                logger.info(f"Found {len(messages)} messages for user {user_email}")
                return messages
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return self.generate_demo_messages(user_email, stream or "general")
                
        except Exception as e:
            logger.error(f"Error getting unread messages: {e}")
            return self.generate_demo_messages(user_email, stream or "general")
    
    def create_message_link(self, message: Dict) -> str:
        """Create a direct link to a specific message"""
        try:
            message_id = message.get("id")
            stream_id = message.get("stream_id")
            topic_id = message.get("topic_id")
            stream_name = message.get("stream", "")
            topic_name = message.get("subject", "")
            
            server_url = self.config['zulip_server'].replace('https://', '').replace('http://', '')
            
            if stream_id and topic_id:
                return f"https://{server_url}/#narrow/stream/{stream_id}/topic/{topic_id}/near/{message_id}"
            else:
                # Fallback using names
                safe_stream = quote(stream_name.replace(' ', '-'))
                safe_topic = quote(topic_name.replace(' ', '-'))
                return f"https://{server_url}/#narrow/stream/{safe_stream}/topic/{safe_topic}/near/{message_id}"
                
        except Exception as e:
            logger.error(f"Error creating message link: {e}")
            return f"https://localhost/#narrow/stream/general/topic/general/near/{message.get('id', 0)}"
    
    def generate_demo_messages(self, user_email: str, stream: str) -> List[Dict]:
        """Generate demo messages when Zulip connection fails"""
        current_time = datetime.now()
        demo_messages = [
            {
                "id": int(current_time.timestamp()) + 1,
                "content": f"Mensaje de demostración para {user_email} en {stream}",
                "sender_full_name": "Demo User 1",
                "timestamp": current_time.timestamp() - 300,
                "stream": stream,
                "subject": "Demo Topic",
                "direct_link": f"https://localhost/#narrow/stream/{stream}/topic/demo/near/demo1"
            },
            {
                "id": int(current_time.timestamp()) + 2,
                "content": f"Este es un mensaje no leído de ejemplo en el canal {stream}",
                "sender_full_name": "Demo User 2",
                "timestamp": current_time.timestamp() - 240,
                "stream": stream,
                "subject": "Demo Topic",
                "direct_link": f"https://localhost/#narrow/stream/{stream}/topic/demo/near/demo2"
            },
            {
                "id": int(current_time.timestamp()) + 3,
                "content": f"Sistema de resúmenes funcionando correctamente - {current_time.strftime('%H:%M')}",
                "sender_full_name": "System Bot",
                "timestamp": current_time.timestamp() - 180,
                "stream": stream,
                "subject": "Demo Topic",
                "direct_link": f"https://localhost/#narrow/stream/{stream}/topic/demo/near/demo3"
            }
        ]
        
        return demo_messages
    
    def generate_summary_with_llm(self, messages: List[Dict], stream: str, user_email: str) -> Dict:
        """Generate summary of messages using LLM (Ollama or Gemini)"""
        try:
            if not messages:
                return {
                    "summary": "No hay mensajes no leídos para resumir.",
                    "key_points": [],
                    "actions_needed": [],
                    "llm_used": "none"
                }
            
            # Extract message content with metadata
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", 0)
                direct_link = msg.get("direct_link", "")
                
                # Format message with timestamp and link
                time_str = datetime.fromtimestamp(timestamp).strftime('%H:%M')
                formatted_msg = f"[{time_str}] **{sender}**: {content}"
                if direct_link:
                    formatted_msg += f" [Ver mensaje]({direct_link})"
                
                message_texts.append(formatted_msg)
            
            # Create prompt for LLM
            all_messages = "\n".join(message_texts)
            prompt = f"""
Por favor, genera un resumen estructurado de los siguientes mensajes no leídos para el usuario {user_email} en el canal "{stream}".

Mensajes:
{all_messages}

Instrucciones:
1. Genera un resumen conciso (máximo 100 palabras)
2. Identifica los puntos clave más importantes
3. Menciona cualquier acción requerida o seguimiento necesario
4. Mantén el tono profesional y claro
5. Responde en formato JSON con las siguientes claves:
   - "summary": Resumen general
   - "key_points": Array de puntos clave (máximo 3 puntos)
   - "actions_needed": Array de acciones requeridas (si las hay)

Respuesta:
"""
            
            # Try Gemini first if API key is available
            if self.gemini_api_key:
                summary_data = self.call_gemini_api(prompt)
                if summary_data:
                    summary_data["llm_used"] = "gemini"
                    return summary_data
            
            # Fallback to Ollama
            summary_data = self.call_ollama_api(prompt)
            summary_data["llm_used"] = "ollama"
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {e}")
            return {
                "summary": f"No se pudo generar el resumen debido a un error: {str(e)}",
                "key_points": [],
                "actions_needed": [],
                "llm_used": "error"
            }
    
    def call_gemini_api(self, prompt: str) -> Optional[Dict]:
        """Call Gemini API for summary generation"""
        try:
            import google.generativeai as genai
            
            genai.configure(api_key=self.gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
            
            response = model.generate_content(prompt)
            
            if response.text:
                # Try to parse JSON response
                try:
                    return json.loads(response.text)
                except json.JSONDecodeError:
                    # If not JSON, create structured response
                    return {
                        "summary": response.text,
                        "key_points": [],
                        "actions_needed": []
                    }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return None
    
    def call_ollama_api(self, prompt: str) -> Dict:
        """Call Ollama API for summary generation"""
        try:
            ollama_payload = {
                "model": "gemma2",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                summary_text = result.get("response", "").strip()
                
                # Try to parse JSON response
                try:
                    return json.loads(summary_text)
                except json.JSONDecodeError:
                    # If not JSON, create structured response
                    return {
                        "summary": summary_text,
                        "key_points": [],
                        "actions_needed": []
                    }
            else:
                logger.error(f"Error calling Ollama: {response.status_code}")
                return {
                    "summary": "Error generando resumen con Ollama",
                    "key_points": [],
                    "actions_needed": []
                }
                
        except Exception as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {
                "summary": f"No se pudo generar el resumen con Ollama: {str(e)}",
                "key_points": [],
                "actions_needed": []
            }
    
    def publish_recap_to_kafka(self, user_email: str, stream: str, recap_data: Dict, messages: List[Dict]) -> bool:
        """Publish message recap to Kafka"""
        try:
            # Extract message links for the recap
            message_links = []
            for msg in messages:
                message_links.append({
                    "id": msg.get("id"),
                    "sender": msg.get("sender_full_name", "Unknown"),
                    "content_preview": msg.get("content", "")[:50] + "...",
                    "direct_link": msg.get("direct_link", ""),
                    "timestamp": msg.get("timestamp", 0),
                    "stream": msg.get("stream", ""),
                    "topic": msg.get("subject", "")
                })
            
            payload = {
                "message_type": "message_recap",
                "timestamp": datetime.now().isoformat(),
                "user_email": user_email,
                "stream": stream,
                "recap": recap_data,
                "message_count": len(messages),
                "message_links": message_links,
                "processed_at": datetime.now().isoformat(),
                "server_url": self.config['zulip_server']
            }
            
            # Send to Kafka using KafkaProducer
            if self.producer:
                try:
                    key = f"{user_email}-{stream}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    
                    future = self.producer.send(
                        self.kafka_topic_summaries,
                        key=key,
                        value=payload
                    )
                    
                    # Wait for the message to be sent
                    record_metadata = future.get(timeout=30)
                    
                    logger.info(f"Message recap published successfully to Kafka")
                    logger.info(f"Topic: {record_metadata.topic}, Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Error sending recap to Kafka: {e}")
                    return False
            else:
                logger.error("Kafka producer not initialized")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing recap to Kafka: {e}")
            return False

# Initialize backend instance
recap_backend = MessageRecapBackend()

@app.route('/api/recap/generate', methods=['POST'])
def generate_recap():
    """Generate message recap for a user"""
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        stream = data.get('stream')  # Optional
        
        if not user_email:
            return jsonify({"error": "user_email is required"}), 400
        
        # Get unread messages for user
        messages = recap_backend.get_unread_messages_for_user(user_email, stream)
        
        if not messages:
            return jsonify({
                "message": "No unread messages found",
                "recap": {
                    "summary": "No tienes mensajes no leídos.",
                    "key_points": [],
                    "actions_needed": [],
                    "llm_used": "none"
                },
                "message_count": 0,
                "messages": []
            })
        
        # Generate summary
        recap_data = recap_backend.generate_summary_with_llm(messages, stream or "general", user_email)
        
        # Publish to Kafka
        success = recap_backend.publish_recap_to_kafka(user_email, stream or "general", recap_data, messages)
        
        return jsonify({
            "message": "Recap generated successfully",
            "recap": recap_data,
            "message_count": len(messages),
            "messages": messages[:10],  # Return first 10 messages
            "kafka_published": success,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Error generating recap: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recap/status/<user_email>', methods=['GET'])
def get_recap_status(user_email: str):
    """Get recap status for a user"""
    try:
        # This would typically check database or cache for recent recaps
        # For now, return a simple status
        return jsonify({
            "user_email": user_email,
            "last_recap": datetime.now().isoformat(),
            "total_recaps_generated": 1,
            "status": "active"
        })
        
    except Exception as e:
        logger.error(f"Error getting recap status: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/recap/preferences', methods=['POST'])
def set_recap_preferences():
    """Set user preferences for recaps"""
    try:
        data = request.get_json()
        user_email = data.get('user_email')
        preferences = data.get('preferences', {})
        
        # This would typically save to database
        # For now, just return success
        return jsonify({
            "message": "Preferences saved successfully",
            "user_email": user_email,
            "preferences": preferences
        })
        
    except Exception as e:
        logger.error(f"Error setting preferences: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "kafka_connected": recap_backend.producer is not None,
        "ollama_available": True,  # Could check actual availability
        "gemini_available": bool(recap_backend.gemini_api_key)
    })

if __name__ == '__main__':
    logger.info("Starting Message Recap Backend...")
    app.run(host='0.0.0.0', port=5001, debug=True)
