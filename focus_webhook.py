#!/usr/bin/env python3
"""
Focus Webhook Server
Receives focus reminder messages and forwards them to Zulip
"""

from flask import Flask, request, jsonify
import logging
import json
import requests
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

class FocusWebhookServer:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize webhook server"""
        self.config = self.load_config(config_file)
        self.webhook_bot = self.get_bot_config("focus-bot") or self.get_bot_config("zzz-bot")
        
    def load_config(self, config_file: str) -> dict:
        """Load bot configuration"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def get_bot_config(self, bot_name: str) -> dict:
        """Get specific bot configuration"""
        for bot in self.config.get("bots", []):
            if bot.get("bot_name") == bot_name:
                return bot
        return {}
    
    def send_to_zulip(self, message: str, stream: str, topic: str) -> bool:
        """Send message to Zulip"""
        try:
            server_url = "http://localhost"
            url = f"{server_url}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.webhook_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type": "stream",
                "to": stream,
                "topic": topic,
                "content": message
            }
            
            response = requests.post(url, headers=headers, json=payload, verify=False)
            
            if response.status_code == 200:
                logger.info(f"Message sent to #{stream}/{topic}")
                return True
            else:
                logger.error(f"Error sending message: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending to Zulip: {e}")
            return False

# Initialize webhook server
webhook_server = FocusWebhookServer()

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Handle incoming webhook requests"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Extract message data
        message = data.get("message", "")
        stream = data.get("stream", "desarrollo")
        topic = data.get("topic", "recordatorio-foco")
        message_type = data.get("type", "focus_reminder")
        
        logger.info(f"Received {message_type} for #{stream}/{topic}")
        
        # Send to Zulip
        success = webhook_server.send_to_zulip(message, stream, topic)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Focus reminder sent",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send to Zulip"
            }), 500
            
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "focus_webhook"
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Focus Webhook Server",
        "version": "1.0.0",
        "endpoints": {
            "/webhook": "POST - Receive focus reminders",
            "/health": "GET - Health check"
        }
    }), 200

if __name__ == "__main__":
    print("="*50)
    print("FOCUS WEBHOOK SERVER")
    print("="*50)
    print("Starting server on http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("="*50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
