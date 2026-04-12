#!/usr/bin/env python3
"""
External Webhook Service
Receives data from outgoing webhook, generates summaries with Ollama, and sends back via incoming webhook
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Any
import re

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class WebhookService:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the webhook service"""
        self.config = self.load_config(config_file)
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "llama3"
        
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
    
    def generate_summary_with_ollama(self, messages: List[Dict], stream: str, topic: str) -> str:
        """Generate summary of messages using Ollama"""
        try:
            # Extract message content
            message_texts = []
            for msg in messages:
                content = msg.get("content", "")
                sender = msg.get("sender_full_name", "Unknown")
                timestamp = msg.get("timestamp", "")
                
                # Format message for summary
                formatted_msg = f"[{sender}]: {content}"
                message_texts.append(formatted_msg)
            
            # Create prompt for Ollama
            all_messages = "\n".join(message_texts)
            prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del stream "{stream}" en el topic "{topic}".

Mensajes:
{all_messages}

Instrucciones:
1. Identifica los puntos principales y temas discutidos
2. Menciona decisiones importantes si las hay
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 200 palabras)

Resumen:
"""
            
            # Call Ollama API
            ollama_payload = {
                "model": self.ollama_model,
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
                summary = result.get("response", "").strip()
                logger.info(f"Generated summary for {stream}/{topic}")
                return summary
            else:
                logger.error(f"Error calling Ollama: {response.status_code}")
                return f"Error generando resumen para {stream}/{topic}"
                
        except Exception as e:
            logger.error(f"Error generating summary with Ollama: {e}")
            return f"No se pudo generar el resumen debido a un error: {str(e)}"
    
    def send_summary_to_zulip(self, stream: str, topic: str, summary: str) -> bool:
        """Send summary back to Zulip via incoming webhook"""
        try:
            url = f"{self.incoming_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Create message content
            message_content = f"""**Resumen Automático** - {stream}/{topic}

{summary}

---
*Generado por IA usando Ollama - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            payload = {
                "type": "stream",
                "to": stream,
                "topic": f"resumen-{topic}",
                "content": message_content
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Summary sent successfully to {stream}/resumen-{topic}")
                return True
            else:
                logger.error(f"Error sending summary to Zulip: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending summary to Zulip: {e}")
            return False

# Initialize service
webhook_service = WebhookService()

@app.route('/webhook/receive', methods=['POST'])
def receive_webhook():
    """Receive webhook data from outgoing webhook"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Verify webhook token if present
        expected_token = webhook_service.outgoing_bot.get("webhook_token")
        if expected_token and data.get("webhook_token") != expected_token:
            return jsonify({"error": "Invalid webhook token"}), 401
        
        # Extract message data
        trigger_type = data.get("trigger_type")
        timestamp = data.get("timestamp")
        message_data = data.get("data", {})
        
        stream = message_data.get("stream")
        topic = message_data.get("topic")
        messages = message_data.get("messages", [])
        
        logger.info(f"Received webhook for {stream}/{topic} with {len(messages)} messages")
        
        # Generate summary
        summary = webhook_service.generate_summary_with_ollama(messages, stream, topic)
        
        # Send summary back to Zulip
        success = webhook_service.send_summary_to_zulip(stream, topic, summary)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Summary generated and sent for {stream}/{topic}",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send summary to Zulip"
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "webhook-service"
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Get service status"""
    try:
        # Check Ollama availability
        ollama_status = "unknown"
        try:
            response = requests.get(f"{webhook_service.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_status = "available"
            else:
                ollama_status = "unavailable"
        except:
            ollama_status = "unreachable"
        
        return jsonify({
            "service": "webhook-service",
            "status": "running",
            "ollama_status": ollama_status,
            "incoming_bot": webhook_service.incoming_bot.get("bot_name"),
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    logger.info("Starting webhook service on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)
