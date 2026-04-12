#!/usr/bin/env python3
"""
LLM Conversation Analyzer
Usa LLM para analizar cambios de conversación y generar mensajes de enfoque
"""

import requests
import json
import logging
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMConversationAnalyzer:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the LLM conversation analyzer"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("llm-analyzer") or self.get_bot_config("zzz-bot")
        self.target_stream = "desarrollo"  # Canal de tecnología
        self.incoming_webhook_url = "http://localhost:5001/webhook"
        
        # Conversation tracking
        self.conversation_history = deque(maxlen=10)
        self.current_context = ""
        self.last_analysis_time = None
        self.last_focus_message = None
        self.analysis_interval = 20  # segundos
        
        # LLM Configuration (Gemma2 local)
        self.llm_url = "http://localhost:11434/api/generate"
        self.llm_model = "gemma2:2b"
        
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
    
    def get_recent_messages(self, limit: int = 5) -> List[Dict]:
        """Get recent messages from the desarrollo stream"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.monitor_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            # Get messages from desarrollo stream
            params = {
                "type": "stream",
                "stream": self.target_stream,
                "narrow": json.dumps([{"operator": "stream", "operand": self.target_stream}])
            }
            
            response = requests.get(url, headers=headers, params=params, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                messages = data.get("messages", [])
                return messages[-limit:]  # Return last N messages
            else:
                logger.error(f"Error getting messages: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting recent messages: {e}")
            return []
    
    def analyze_conversation_with_llm(self, messages: List[Dict]) -> Dict:
        """Analyze conversation using LLM to detect topic changes"""
        if not messages:
            return {"topic_change": False, "reason": "No messages"}
        
        # Prepare conversation context
        conversation_text = "\n".join([
            f"{msg.get('sender_full_name', 'Unknown')}: {msg.get('content', '')}"
            for msg in messages
        ])
        
        # Create LLM prompt
        prompt = f"""Analiza la siguiente conversación del canal de tecnología/desarrollo:

{conversation_text}

Responde en formato JSON con las siguientes claves:
- "main_topic": tema principal de la conversación
- "topic_change": true/false si hay un cambio de tema significativo
- "previous_topic": tema anterior (si aplica)
- "new_topic": nuevo tema (si hay cambio)
- "change_reason": razón del cambio de tema
- "focus_needed": true/false si se necesita un recordatorio de foco
- "suggestion": sugerencia para mantener la conversación enfocada

Ejemplo de respuesta:
{{"main_topic": "desarrollo API REST", "topic_change": true, "previous_topic": "React frontend", "new_topic": "políticas empresa", "change_reason": "cambio repentino a tema no técnico", "focus_needed": true, "suggestion": "sugerir nuevo topic para tema no técnico"}}"""
        
        try:
            # Call LLM
            payload = {
                "model": self.llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 500
                }
            }
            
            response = requests.post(self.llm_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get("response", "")
                
                # Try to parse JSON from LLM response
                try:
                    # Extract JSON from response
                    start_idx = llm_response.find("{")
                    end_idx = llm_response.rfind("}") + 1
                    
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = llm_response[start_idx:end_idx]
                        analysis = json.loads(json_str)
                        
                        # Add metadata
                        analysis["timestamp"] = datetime.now().isoformat()
                        analysis["message_count"] = len(messages)
                        
                        return analysis
                    else:
                        logger.error("Could not extract JSON from LLM response")
                        return {"topic_change": False, "reason": "Invalid LLM response format"}
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    logger.error(f"LLM response: {llm_response}")
                    return {"topic_change": False, "reason": "JSON decode error"}
                    
            else:
                logger.error(f"LLM API error: {response.status_code}")
                return {"topic_change": False, "reason": "LLM API error"}
                
        except Exception as e:
            logger.error(f"Error analyzing with LLM: {e}")
            return {"topic_change": False, "reason": "Analysis error"}
    
    def generate_focus_message(self, analysis: Dict) -> str:
        """Generate focus message based on LLM analysis"""
        if not analysis.get("focus_needed", False):
            return ""
        
        main_topic = analysis.get("main_topic", "conversación técnica")
        previous_topic = analysis.get("previous_topic", "")
        new_topic = analysis.get("new_topic", "")
        suggestion = analysis.get("suggestion", "")
        
        focus_message = f"""**@all Mantengamos el foco en la conversación técnica** :light_bulb:

**Contexto actual:** {main_topic}
**Tema anterior:** {previous_topic}
**Nueva dirección:** {new_topic}

**Análisis LLM:** {analysis.get('change_reason', 'Cambio de tema detectado')}

**Sugerencia:** {suggestion}

**Para mejor organización:**
- Si es un tema técnico relacionado, continuemos aquí
- Si es un tema diferente (no técnico), consideren abrir un nuevo topic
- Para temas variados, usen threads separados

**Canal:** #{self.target_stream} | **Timestamp:** {datetime.now().strftime('%H:%M')}

---
*Análisis automático con LLM - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return focus_message
    
    def send_focus_reminder(self, focus_message: str, analysis: Dict) -> bool:
        """Send focus reminder via incoming webhook"""
        if not focus_message:
            return False
        
        try:
            payload = {
                "message": focus_message,
                "stream": self.target_stream,
                "topic": "recordatorio-foco-llm",
                "type": "llm_focus_reminder",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.incoming_webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Focus reminder sent via incoming webhook")
                self.last_focus_message = datetime.now()
                return True
            else:
                logger.error(f"Error sending focus reminder: {response.status_code}")
                # Fallback to direct API
                return self.send_message_via_api(focus_message)
                
        except Exception as e:
            logger.error(f"Error sending focus reminder: {e}")
            return False
    
    def send_message_via_api(self, content: str, topic: str = "recordatorio-foco-llm") -> bool:
        """Send message directly via Zulip API (fallback)"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.monitor_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": topic,
                "content": content
            }
            
            response = requests.post(url, headers=headers, json=payload, verify=False)
            
            if response.status_code == 200:
                logger.info("Message sent via API (fallback)")
                return True
            else:
                logger.error(f"Error sending message via API: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message via API: {e}")
            return False
    
    def should_analyze(self) -> bool:
        """Check if we should run analysis"""
        if not self.last_analysis_time:
            return True
        
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= self.analysis_interval
    
    def should_send_focus_reminder(self) -> bool:
        """Check if we should send a focus reminder"""
        if not self.last_focus_message:
            return True
        
        # Wait at least 5 minutes between reminders
        time_since_last = datetime.now() - self.last_focus_message
        return time_since_last.total_seconds() >= 300
    
    def analyze_and_act(self):
        """Main analysis and action method"""
        if not self.should_analyze():
            return
        
        logger.info("Running conversation analysis...")
        
        # Get recent messages
        messages = self.get_recent_messages(limit=5)
        
        if not messages:
            logger.info("No messages to analyze")
            self.last_analysis_time = datetime.now()
            return
        
        # Skip if all messages are from bots
        human_messages = [msg for msg in messages if "bot" not in msg.get("sender_full_name", "").lower()]
        if not human_messages:
            logger.info("No human messages to analyze")
            self.last_analysis_time = datetime.now()
            return
        
        # Analyze with LLM
        analysis = self.analyze_conversation_with_llm(human_messages)
        
        logger.info(f"Analysis result: {analysis.get('topic_change', False)} - {analysis.get('main_topic', 'Unknown')}")
        
        # Update analysis time
        self.last_analysis_time = datetime.now()
        
        # Generate and send focus message if needed
        if analysis.get("focus_needed", False) and self.should_send_focus_reminder():
            focus_message = self.generate_focus_message(analysis)
            
            if focus_message:
                logger.info("Sending focus reminder...")
                self.send_focus_reminder(focus_message, analysis)
        
        # Store conversation context
        self.conversation_history.extend(human_messages)
        self.current_context = analysis.get("main_topic", "")
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info(f"Starting LLM conversation analysis for #{self.target_stream}")
        logger.info(f"Analysis interval: {self.analysis_interval} seconds")
        
        while True:
            try:
                self.analyze_and_act()
                time.sleep(self.analysis_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def test_llm_connection(self):
        """Test LLM connection"""
        try:
            payload = {
                "model": self.llm_model,
                "prompt": "Responde con 'OK' si puedes leer esto.",
                "stream": False,
                "options": {"max_tokens": 10}
            }
            
            response = requests.post(self.llm_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"LLM connection test: {result.get('response', 'No response')}")
                return True
            else:
                logger.error(f"LLM connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"LLM connection error: {e}")
            return False

def main():
    """Main function"""
    analyzer = LLMConversationAnalyzer()
    
    try:
        print("="*60)
        print("LLM CONVERSATION ANALYZER")
        print("="*60)
        print(f"Target channel: #{analyzer.target_stream}")
        print(f"Analysis interval: {analyzer.analysis_interval} seconds")
        print(f"LLM model: {analyzer.llm_model}")
        print("="*60)
        
        # Test LLM connection
        print("\nTesting LLM connection...")
        if not analyzer.test_llm_connection():
            print("LLM connection failed. Please check if Gemma2 is running on localhost:11434")
            return
        
        print("LLM connection successful!")
        
        # Test analysis
        print("\nTesting conversation analysis...")
        analyzer.analyze_and_act()
        
        # Start monitoring
        response = input("\nStart continuous monitoring? (y/n): ").lower()
        if response == 'y':
            print("\nStarting continuous monitoring... (Ctrl+C to stop)")
            analyzer.start_monitoring()
        else:
            print("Monitoring not started.")
            
    except KeyboardInterrupt:
        logger.info("Analyzer stopped by user")
    except Exception as e:
        logger.error(f"Analyzer error: {e}")

if __name__ == "__main__":
    main()
