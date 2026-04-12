#!/usr/bin/env python3
"""
Contextual Focus Analyzer
Analiza conversaciones cada 20 segundos y alerta sobre cambios de tema
enviando mensajes para volver al tema anterior
"""

import requests
import json
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextualFocusAnalyzer:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the contextual focus analyzer"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("xxx-bot")  # Use webhook_outbound bot
        self.target_stream = "desarrollo"
        self.webhook_url = "http://localhost:5001/webhook"
        
        # Topic tracking
        self.conversation_history = deque(maxlen=10)
        self.current_main_topic = ""
        self.topic_keywords = set()
        self.last_alert_time = None
        self.last_analysis_time = None
        self.analysis_interval = 20  # segundos
        
        # Topic categories for better detection
        self.tech_categories = {
            'programación': ['python', 'java', 'javascript', 'react', 'vue', 'angular', 'codigo', 'programación', 'algoritmo'],
            'base_datos': ['database', 'sql', 'postgresql', 'mysql', 'mongodb', 'redis', 'query', 'datos'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'cloud', 'deploy', 'ci/cd', 'servidor'],
            'frontend': ['html', 'css', 'react', 'vue', 'angular', 'ui', 'ux', 'frontend', 'interfaz'],
            'backend': ['api', 'rest', 'graphql', 'microservicios', 'backend', 'servidor', 'endpoint'],
            'seguridad': ['seguridad', 'autenticación', 'jwt', 'oauth', 'encriptación', 'vulnerabilidad'],
            'testing': ['test', 'testing', 'unitario', 'integración', 'e2e', 'pytest', 'jest'],
            'performance': ['optimización', 'rendimiento', 'performance', 'caching', 'escalabilidad']
        }
        
        # Non-tech indicators
        self.non_tech_indicators = {
            'empresa': ['empresa', 'trabajo', 'jefe', 'reunión', 'política', 'salario', 'vacaciones'],
            'personal': ['familia', 'personal', 'casa', 'comida', 'clima', 'deporte', 'salud'],
            'general': ['noticias', 'general', 'random', 'off-topic', 'charla', 'conversación']
        }
        
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
    
    def extract_topic_category(self, message: str) -> tuple:
        """Extract topic category and keywords from message"""
        message_lower = message.lower()
        words = re.findall(r'\b\w+\b', message_lower)
        
        # Check tech categories
        for category, keywords in self.tech_categories.items():
            matches = [word for word in words if word in keywords]
            if matches:
                return ('tech', category, set(matches))
        
        # Check non-tech categories
        for category, keywords in self.non_tech_indicators.items():
            matches = [word for word in words if word in keywords]
            if matches:
                return ('non_tech', category, set(matches))
        
        # Default: no specific category
        return ('general', 'unknown', set())
    
    def analyze_conversation_context(self, messages: List[Dict]) -> Dict:
        """Analyze conversation context and detect topic changes"""
        if not messages:
            return {"topic_change": False, "reason": "No messages"}
        
        # Get the most recent messages (last 3)
        recent_messages = messages[-3:]
        
        # Analyze each message
        message_analysis = []
        for msg in recent_messages:
            content = msg.get("content", "")
            sender = msg.get("sender_full_name", "Unknown")
            
            topic_type, category, keywords = self.extract_topic_category(content)
            
            message_analysis.append({
                "sender": sender,
                "content": content[:100] + "..." if len(content) > 100 else content,
                "topic_type": topic_type,
                "category": category,
                "keywords": keywords
            })
        
        # Determine main topic from recent messages
        tech_count = sum(1 for analysis in message_analysis if analysis["topic_type"] == "tech")
        non_tech_count = sum(1 for analysis in message_analysis if analysis["topic_type"] == "non_tech")
        
        # Detect topic change
        topic_change = False
        change_reason = ""
        current_topic = ""
        previous_topic = ""
        
        if not self.current_main_topic:
            # Establish initial topic
            if tech_count >= non_tech_count:
                current_topic = "discusión técnica"
            else:
                current_topic = "conversación no técnica"
            
            self.current_main_topic = current_topic
            self.topic_keywords = set()
            for analysis in message_analysis:
                self.topic_keywords.update(analysis["keywords"])
            
            return {
                "topic_change": False,
                "current_topic": current_topic,
                "message_analysis": message_analysis,
                "reason": "Initial topic established"
            }
        
        # Check for topic change
        if tech_count == 0 and non_tech_count > 0:
            # Changed to non-tech
            topic_change = True
            change_reason = "Cambio a tema no técnico"
            current_topic = "conversación no técnica"
            previous_topic = self.current_main_topic
            
        elif non_tech_count == 0 and tech_count > 0:
            # Changed to tech
            topic_change = True
            change_reason = "Cambio a tema técnico"
            current_topic = "discusión técnica"
            previous_topic = self.current_main_topic
        
        elif tech_count > 0 and non_tech_count > 0:
            # Mixed topics - check if it's a significant change
            if self.current_main_topic == "discusión técnica" and non_tech_count >= tech_count:
                topic_change = True
                change_reason = "Mezcla de temas con predominio no técnico"
                current_topic = "conversación mixta"
                previous_topic = self.current_main_topic
            elif self.current_main_topic == "conversación no técnica" and tech_count >= non_tech_count:
                topic_change = True
                change_reason = "Mezcla de temas con predominio técnico"
                current_topic = "conversación mixta"
                previous_topic = self.current_main_topic
        
        return {
            "topic_change": topic_change,
            "change_reason": change_reason,
            "current_topic": current_topic,
            "previous_topic": previous_topic,
            "message_analysis": message_analysis,
            "tech_count": tech_count,
            "non_tech_count": non_tech_count
        }
    
    def generate_contextual_alert(self, analysis: Dict) -> str:
        """Generate contextual alert message"""
        if not analysis.get("topic_change", False):
            return ""
        
        current_topic = analysis.get("current_topic", "")
        previous_topic = analysis.get("previous_topic", "")
        change_reason = analysis.get("change_reason", "")
        message_analysis = analysis.get("message_analysis", [])
        
        # Get the last message that triggered the change
        last_message = message_analysis[-1] if message_analysis else {}
        last_sender = last_message.get("sender", "Unknown")
        last_content = last_message.get("content", "")
        
        alert_message = f"""**@all Alerta de Cambio de Tema** :warning:

**Tema anterior:** {previous_topic}
**Nuevo tema detectado:** {current_topic}
**Razón:** {change_reason}

**Último mensaje:** {last_sender}: "{last_content}"

**Para mantener el enfoque:**
- Si el cambio es intencional, pueden continuar
- Si fue accidental, consideren volver al tema: {previous_topic}
- Para temas diferentes, sugiero abrir un nuevo topic

**Análisis contextual:**
- Mensajes técnicos: {analysis.get('tech_count', 0)}
- Mensajes no técnicos: {analysis.get('non_tech_count', 0)}

**Canal:** #{self.target_stream} | **Timestamp:** {datetime.now().strftime('%H:%M')}

---
*Alerta automática contextual - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return alert_message
    
    def get_recent_messages(self, limit: int = 5) -> List[Dict]:
        """Get recent messages from the desarrollo stream"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Get messages from desarrollo stream
            params = {
                "type": "stream",
                "stream": self.target_stream,
                "narrow": json.dumps([{"operator": "stream", "operand": self.target_stream}]),
                "num_before": limit,
                "num_after": 0,
                "anchor": "newest"
            }
            
            response = requests.get(url, auth=auth, params=params, verify=False)
            
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
    
    def send_contextual_alert(self, alert_message: str, analysis: Dict) -> bool:
        """Send contextual alert via webhook"""
        if not alert_message:
            return False
        
        try:
            payload = {
                "message": alert_message,
                "stream": self.target_stream,
                "topic": "alerta-cambio-tema",
                "type": "contextual_focus_alert",
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Contextual alert sent via webhook")
                self.last_alert_time = datetime.now()
                return True
            else:
                logger.error(f"Error sending contextual alert: {response.status_code}")
                # Fallback to direct API
                return self.send_message_via_api(alert_message)
                
        except Exception as e:
            logger.error(f"Error sending contextual alert: {e}")
            return False
    
    def send_message_via_api(self, content: str, topic: str = "alerta-cambio-tema") -> bool:
        """Send message directly via Zulip API (fallback)"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": topic,
                "content": content
            }
            
            response = requests.post(url, auth=auth, data=payload, verify=False)
            
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
    
    def should_send_alert(self) -> bool:
        """Check if we should send an alert"""
        if not self.last_alert_time:
            return True
        
        # Wait at least 3 minutes between alerts
        time_since_last = datetime.now() - self.last_alert_time
        return time_since_last.total_seconds() >= 180
    
    def analyze_and_alert(self):
        """Main analysis and alert method"""
        if not self.should_analyze():
            return
        
        logger.info("Running contextual conversation analysis...")
        
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
        
        # Analyze conversation context
        analysis = self.analyze_conversation_context(human_messages)
        
        logger.info(f"Analysis result: {analysis.get('topic_change', False)} - {analysis.get('current_topic', 'Unknown')}")
        
        # Update analysis time
        self.last_analysis_time = datetime.now()
        
        # Generate and send alert if topic changed
        if analysis.get("topic_change", False) and self.should_send_alert():
            alert_message = self.generate_contextual_alert(analysis)
            
            if alert_message:
                logger.info("Sending contextual alert...")
                self.send_contextual_alert(alert_message, analysis)
                
                # Update current topic
                self.current_main_topic = analysis.get("current_topic", "")
        
        # Store conversation context
        self.conversation_history.extend(human_messages)
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info(f"Starting contextual focus analysis for #{self.target_stream}")
        logger.info(f"Analysis interval: {self.analysis_interval} seconds")
        logger.info("Alerts will be sent when topic changes are detected")
        
        while True:
            try:
                self.analyze_and_alert()
                time.sleep(self.analysis_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def test_analyzer(self):
        """Test the contextual analyzer"""
        logger.info("Testing contextual focus analyzer...")
        
        # Get recent messages
        messages = self.get_recent_messages(limit=3)
        
        if not messages:
            logger.info("No messages available for testing")
            return
        
        # Analyze
        analysis = self.analyze_conversation_context(messages)
        
        print(f"\nTest Analysis Results:")
        print(f"Topic Change: {analysis.get('topic_change', False)}")
        print(f"Current Topic: {analysis.get('current_topic', 'Unknown')}")
        print(f"Previous Topic: {analysis.get('previous_topic', 'Unknown')}")
        print(f"Change Reason: {analysis.get('change_reason', 'None')}")
        print(f"Tech Count: {analysis.get('tech_count', 0)}")
        print(f"Non-Tech Count: {analysis.get('non_tech_count', 0)}")
        
        print(f"\nMessage Analysis:")
        for i, msg_analysis in enumerate(analysis.get('message_analysis', []), 1):
            print(f"  {i}. {msg_analysis['sender']}: {msg_analysis['topic_type']} - {msg_analysis['category']}")
        
        # Generate alert if needed
        if analysis.get("topic_change", False):
            alert = self.generate_contextual_alert(analysis)
            print(f"\nGenerated Alert:")
            print(alert[:200] + "..." if len(alert) > 200 else alert)

def main():
    """Main function"""
    analyzer = ContextualFocusAnalyzer()
    
    try:
        print("="*60)
        print("CONTEXTUAL FOCUS ANALYZER")
        print("="*60)
        print(f"Target channel: #{analyzer.target_stream}")
        print(f"Analysis interval: {analyzer.analysis_interval} seconds")
        print("Alerts for topic changes: ENABLED")
        print("="*60)
        
        # Test first
        print("\nRunning analysis test...")
        analyzer.test_analyzer()
        
        # Ask user if they want to start monitoring
        response = input("\nStart real-time monitoring? (y/n): ").lower()
        if response == 'y':
            print("\nStarting contextual monitoring... (Ctrl+C to stop)")
            analyzer.start_monitoring()
        else:
            print("Monitoring not started.")
            
    except KeyboardInterrupt:
        logger.info("Analyzer stopped by user")
    except Exception as e:
        logger.error(f"Analyzer error: {e}")

if __name__ == "__main__":
    main()
