#!/usr/bin/env python3
"""
Webhook Service with Kafka Support
Alternative Flask service that works with Kafka topics
"""

from flask import Flask, request, jsonify
import requests
import json
import logging
import subprocess
from datetime import datetime
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class KafkaWebhookService:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the webhook service with Kafka support"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.kafka_bootstrap_servers = "localhost:9092"
        self.kafka_topic_unread = "zulip-unread-messages"
        self.kafka_topic_summaries = "zulip-summaries"
        self.ollama_url = "http://localhost:11434"
        self.ollama_model = "gemma2:2b"
        
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
    
    def publish_summary_to_kafka(self, stream: str, topic: str, summary: str, original_data: Dict) -> bool:
        """Publish summary to Kafka summary topic"""
        try:
            payload = {
                "message_type": "summary",
                "timestamp": datetime.now().isoformat(),
                "original_stream": stream,
                "original_topic": topic,
                "summary": summary,
                "original_message_count": original_data.get("message_count", 0),
                "processed_at": datetime.now().isoformat(),
                "webhook_token": self.outgoing_bot.get("webhook_token")
            }
            
            # Convert to JSON string for Kafka
            message_json = json.dumps(payload)
            
            # Send to Kafka using docker exec
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {self.kafka_topic_summaries}"
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                logger.info(f"Summary published successfully to Kafka topic '{self.kafka_topic_summaries}'")
                return True
            else:
                logger.error(f"Error publishing summary to Kafka: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing summary to Kafka: {e}")
            return False

# Initialize service
webhook_service = KafkaWebhookService()

@app.route('/webhook/receive', methods=['POST'])
def receive_webhook():
    """Receive webhook data and process with Kafka"""
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
        
        # Send summary to Kafka
        success = webhook_service.publish_summary_to_kafka(stream, topic, summary, message_data)
        
        if success:
            return jsonify({
                "status": "success",
                "message": f"Summary generated and sent to Kafka for {stream}/{topic}",
                "timestamp": datetime.now().isoformat(),
                "kafka_topic": webhook_service.kafka_topic_summaries
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send summary to Kafka"
            }), 500
            
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return jsonify({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }), 500

@app.route('/kafka/send-unread', methods=['POST'])
def send_unread_to_kafka():
    """Direct endpoint to send unread messages to Kafka"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Validate required fields
        required_fields = ["stream", "topic", "messages"]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Create payload for Kafka
        payload = {
            "trigger_type": "unread_messages",
            "timestamp": datetime.now().isoformat(),
            "stream": data.get("stream"),
            "topic": data.get("topic"),
            "messages": data.get("messages", []),
            "message_count": len(data.get("messages", [])),
            "webhook_token": webhook_service.outgoing_bot.get("webhook_token")
        }
        
        # Send to Kafka
        message_json = json.dumps(payload)
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic {webhook_service.kafka_topic_unread}"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            return jsonify({
                "status": "success",
                "message": f"Unread messages sent to Kafka topic '{webhook_service.kafka_topic_unread}'",
                "kafka_topic": webhook_service.kafka_topic_unread
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": f"Error sending to Kafka: {result.stderr}"
            }), 500
            
    except Exception as e:
        logger.error(f"Error sending unread to Kafka: {e}")
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
        "service": "webhook-service-kafka",
        "kafka_topics": {
            "unread": webhook_service.kafka_topic_unread,
            "summaries": webhook_service.kafka_topic_summaries
        }
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
        
        # Check Kafka topics
        kafka_status = "unknown"
        try:
            cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-topics", "--bootstrap-server", "localhost:9092",
                "--list"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
                if webhook_service.kafka_topic_unread in topics and webhook_service.kafka_topic_summaries in topics:
                    kafka_status = "available"
                else:
                    kafka_status = "topics_missing"
            else:
                kafka_status = "unavailable"
        except:
            kafka_status = "unreachable"
        
        return jsonify({
            "service": "webhook-service-kafka",
            "status": "running",
            "ollama_status": ollama_status,
            "kafka_status": kafka_status,
            "kafka_topics": {
                "unread": webhook_service.kafka_topic_unread,
                "summaries": webhook_service.kafka_topic_summaries
            },
            "bots": {
                "outgoing": webhook_service.outgoing_bot.get("bot_name"),
                "incoming": webhook_service.incoming_bot.get("bot_name")
            },
            "timestamp": datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    logger.info("Starting webhook service with Kafka support on port 8080...")
    app.run(host="0.0.0.0", port=8080, debug=True)
