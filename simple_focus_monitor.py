#!/usr/bin/env python3
"""
Simple Focus Monitor (No LLM)
Vigila el canal desarrollo y mantiene el foco sin usar LLM
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

class SimpleFocusMonitor:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the simple focus monitor"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("zzz-bot")
        self.target_stream = "desarrollo"
        self.webhook_url = "http://localhost:5001/webhook"
        
        # Topic tracking
        self.current_topic = ""
        self.topic_keywords = set()
        self.conversation_history = deque(maxlen=10)
        self.last_focus_message = None
        self.last_analysis_time = None
        self.analysis_interval = 20  # segundos
        
        # Technology keywords for topic detection
        self.tech_keywords = {
            'programación', 'codigo', 'software', 'desarrollo', 'api', 'base de datos',
            'frontend', 'backend', 'javascript', 'python', 'java', 'react', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'cloud', 'devops', 'git',
            'algoritmo', 'framework', 'libreria', 'bug', 'debug', 'test', 'deploy',
            'servidor', 'cliente', 'microservicios', 'arquitectura', 'seguridad',
            'performance', 'optimización', 'escalabilidad', 'integración'
        }
        
        # Non-tech keywords that indicate topic drift
        self.non_tech_keywords = {
            'empresa', 'política', 'salario', 'vacaciones', 'reunión', 'jefe',
            'comida', 'clima', 'deporte', 'noticias', 'personal', 'familia',
            'finanzas', 'bancos', 'impuestos', 'seguro', 'médico', 'salud'
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
    
    def extract_keywords(self, message: str) -> set:
        """Extract keywords from message"""
        # Convert to lowercase and remove punctuation
        cleaned = re.sub(r'[^\w\s]', ' ', message.lower())
        words = cleaned.split()
        
        # Filter keywords
        tech_words = {word for word in words if word in self.tech_keywords}
        non_tech_words = {word for word in words if word in self.non_tech_keywords}
        
        return tech_words.union(non_tech_words)
    
    def calculate_topic_similarity(self, keywords1: set, keywords2: set) -> float:
        """Calculate similarity between two sets of keywords"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_topic_change(self, message: str) -> bool:
        """Detect if the message represents a topic change"""
        current_keywords = self.extract_keywords(message)
        
        # If we don't have a current topic, establish one
        if not self.current_topic:
            self.current_topic = self.extract_topic_summary(message)
            self.topic_keywords = current_keywords
            logger.info(f"New topic established: {self.current_topic}")
            return False
        
        # Calculate similarity with current topic
        similarity = self.calculate_topic_similarity(current_keywords, self.topic_keywords)
        
        # Check for non-tech keywords (strong indicator of topic drift)
        has_non_tech = any(word in self.non_tech_keywords for word in current_keywords)
        
        # Consider it a topic change if:
        # 1. Similarity is low (< 0.3)
        # 2. OR has non-tech keywords and low similarity (< 0.5)
        if similarity < 0.3 or (has_non_tech and similarity < 0.5):
            logger.info(f"Topic change detected! Similarity: {similarity:.2f}, Non-tech: {has_non_tech}")
            return True
        
        return False
    
    def extract_topic_summary(self, message: str) -> str:
        """Extract a brief summary of the topic from message"""
        words = message.split()[:8]
        tech_words = [word for word in words if word.lower() in self.tech_keywords]
        
        if tech_words:
            return f"Discusión sobre {', '.join(tech_words[:3])}"
        
        return " ".join(words[:5]) + "..."
    
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
    
    def generate_focus_message(self, original_topic: str, new_topic: str) -> str:
        """Generate focus reminder message"""
        focus_message = f"""**@all Mantengamos el foco en la conversación técnica** :light_bulb:

**Tema actual:** {original_topic}
**Nueva dirección detectada:** {new_topic}

**Para mejor organización:**
- Si es un tema técnico relacionado, continuemos aquí
- Si es un tema diferente (no técnico), consideren abrir un nuevo topic
- Para temas variados, usen threads separados

**Canal:** #{self.target_stream} | **Timestamp:** {datetime.now().strftime('%H:%M')}

---
*Recordatorio automático - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        return focus_message
    
    def send_focus_reminder(self, focus_message: str) -> bool:
        """Send focus reminder via webhook"""
        try:
            payload = {
                "message": focus_message,
                "stream": self.target_stream,
                "topic": "recordatorio-foco",
                "type": "simple_focus_reminder",
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(self.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Focus reminder sent via webhook")
                self.last_focus_message = datetime.now()
                return True
            else:
                logger.error(f"Error sending focus reminder: {response.status_code}")
                # Fallback to direct API
                return self.send_message_via_api(focus_message)
                
        except Exception as e:
            logger.error(f"Error sending focus reminder: {e}")
            return False
    
    def send_message_via_api(self, content: str, topic: str = "recordatorio-foco") -> bool:
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
        
        # Analyze the most recent message
        latest_message = human_messages[-1]
        message_content = latest_message.get("content", "")
        sender = latest_message.get("sender_full_name", "Unknown")
        
        logger.info(f"Analyzing message from {sender}: {message_content[:100]}...")
        
        # Update analysis time
        self.last_analysis_time = datetime.now()
        
        # Check for topic change
        if self.detect_topic_change(message_content):
            new_topic = self.extract_topic_summary(message_content)
            
            if self.should_send_focus_reminder():
                logger.info(f"Sending focus reminder: {self.current_topic} -> {new_topic}")
                
                focus_message = self.generate_focus_message(self.current_topic, new_topic)
                self.send_focus_reminder(focus_message)
                
                # Update current topic
                self.current_topic = new_topic
                self.topic_keywords = self.extract_keywords(message_content)
        
        # Store conversation context
        self.conversation_history.extend(human_messages)
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info(f"Starting simple focus monitoring for #{self.target_stream}")
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
    
    def test_monitor(self):
        """Test the monitor with sample messages"""
        logger.info("Testing simple focus monitor...")
        
        test_messages = [
            "Estoy trabajando en una nueva API REST con Python y FastAPI",
            "Alguien sabe cómo optimizar el rendimiento de PostgreSQL?",
            "Qué opinan de las nuevas políticas de trabajo remoto en la empresa?",
            "Volviendo al tema técnico, necesito ayuda con Docker para mi aplicación",
            "El frontend en React está dando problemas de rendimiento"
        ]
        
        for i, message in enumerate(test_messages):
            logger.info(f"Test {i+1}: {message}")
            
            if self.detect_topic_change(message):
                new_topic = self.extract_topic_summary(message)
                logger.info(f"  -> Topic change detected: {new_topic}")
                
                if self.current_topic:
                    logger.info(f"  -> Would send focus reminder: {self.current_topic} -> {new_topic}")
                
                self.current_topic = new_topic
                self.topic_keywords = self.extract_keywords(message)
            else:
                logger.info("  -> Same topic, no action needed")
            
            print()

def main():
    """Main function"""
    monitor = SimpleFocusMonitor()
    
    try:
        print("="*60)
        print("SIMPLE FOCUS MONITOR (No LLM)")
        print("="*60)
        print(f"Target channel: #{monitor.target_stream}")
        print(f"Analysis interval: {monitor.analysis_interval} seconds")
        print("="*60)
        
        # Test first
        print("\nRunning tests...")
        monitor.test_monitor()
        
        # Ask user if they want to start monitoring
        response = input("\nStart real-time monitoring? (y/n): ").lower()
        if response == 'y':
            print("\nStarting monitoring... (Ctrl+C to stop)")
            monitor.start_monitoring()
        else:
            print("Monitoring not started.")
            
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {e}")

if __name__ == "__main__":
    main()
