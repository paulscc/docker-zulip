#!/usr/bin/env python3
"""
Incoming Focus Webhook Server
Recibe mensajes de enfoque del LLM analyzer y los envía a Zulip
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

class IncomingFocusWebhookServer:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize incoming webhook server"""
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
            server_url = self.webhook_bot.get('server_url', 'https://localhost:443')
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
    
    def log_focus_event(self, analysis: dict):
        """Log focus event for tracking"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "main_topic": analysis.get("main_topic", "Unknown"),
                "topic_change": analysis.get("topic_change", False),
                "focus_needed": analysis.get("focus_needed", False),
                "previous_topic": analysis.get("previous_topic", ""),
                "new_topic": analysis.get("new_topic", ""),
                "change_reason": analysis.get("change_reason", "")
            }
            
            # Log to file for tracking
            with open("focus_events.log", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
                
            logger.info(f"Focus event logged: {log_entry['main_topic']}")
            
        except Exception as e:
            logger.error(f"Error logging focus event: {e}")

# Initialize webhook server
webhook_server = IncomingFocusWebhookServer()

@app.route('/webhook', methods=['POST'])
def handle_incoming_webhook():
    """Handle incoming focus reminder requests from LLM analyzer"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data received"}), 400
        
        # Extract message data
        message = data.get("message", "")
        stream = data.get("stream", "desarrollo")
        topic = data.get("topic", "recordatorio-foco-llm")
        message_type = data.get("type", "llm_focus_reminder")
        analysis = data.get("analysis", {})
        
        logger.info(f"Received {message_type} for #{stream}/{topic}")
        logger.info(f"Analysis: {analysis.get('main_topic', 'Unknown')} - Change: {analysis.get('topic_change', False)}")
        
        # Log the focus event
        webhook_server.log_focus_event(analysis)
        
        # Send to Zulip
        success = webhook_server.send_to_zulip(message, stream, topic)
        
        if success:
            return jsonify({
                "status": "success",
                "message": "LLM focus reminder sent successfully",
                "timestamp": datetime.now().isoformat(),
                "analysis": {
                    "main_topic": analysis.get("main_topic"),
                    "topic_change": analysis.get("topic_change"),
                    "focus_needed": analysis.get("focus_needed")
                }
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send focus reminder to Zulip"
            }), 500
            
    except Exception as e:
        logger.error(f"Incoming webhook error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/webhook/test', methods=['POST'])
def test_webhook():
    """Test endpoint for webhook functionality"""
    try:
        test_message = """**@all Test de recordatorio de foco** :test:

Este es un mensaje de prueba del sistema de monitoreo LLM.

**Tema de prueba:** Desarrollo de software
**Estado:** Sistema funcionando correctamente

*Mensaje de prueba - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        success = webhook_server.send_to_zulip(
            test_message, 
            "desarrollo", 
            "test-webhook"
        )
        
        if success:
            return jsonify({
                "status": "success",
                "message": "Test message sent successfully"
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Failed to send test message"
            }), 500
            
    except Exception as e:
        logger.error(f"Test webhook error: {e}")
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
        "service": "incoming_focus_webhook",
        "version": "1.0.0"
    }), 200

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get focus event statistics"""
    try:
        # Read focus events log
        events = []
        try:
            with open("focus_events.log", "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        events.append(json.loads(line.strip()))
        except FileNotFoundError:
            events = []
        
        # Calculate statistics
        total_events = len(events)
        topic_changes = sum(1 for e in events if e.get("topic_change", False))
        focus_reminders_sent = sum(1 for e in events if e.get("focus_needed", False))
        
        # Recent events (last hour)
        recent_time = datetime.now().timestamp() - 3600  # 1 hour ago
        recent_events = [
            e for e in events 
            if datetime.fromisoformat(e.get("timestamp", "")).timestamp() > recent_time
        ]
        
        return jsonify({
            "total_events": total_events,
            "topic_changes_detected": topic_changes,
            "focus_reminders_sent": focus_reminders_sent,
            "recent_events_last_hour": len(recent_events),
            "latest_topics": [e.get("main_topic", "Unknown") for e in events[-5:]][::-1]
        }), 200
        
    except Exception as e:
        logger.error(f"Stats error: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "Incoming Focus Webhook Server",
        "version": "1.0.0",
        "description": "Receives LLM focus reminders and forwards them to Zulip",
        "endpoints": {
            "/webhook": "POST - Receive focus reminders from LLM analyzer",
            "/webhook/test": "POST - Test webhook functionality",
            "/health": "GET - Health check",
            "/stats": "GET - Focus event statistics"
        }
    }), 200

if __name__ == "__main__":
    print("="*60)
    print("INCOMING FOCUS WEBHOOK SERVER")
    print("="*60)
    print("Starting server on http://localhost:5001")
    print("Port: 5001 (different from outgoing webhook)")
    print("Press Ctrl+C to stop")
    print("="*60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
