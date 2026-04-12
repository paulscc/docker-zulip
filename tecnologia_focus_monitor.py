#!/usr/bin/env python3
"""
Tecnología Focus Monitor
Vigila el canal 'desarrollo' (tecnología) y mantiene el foco en la conversación original
"""

import requests
import json
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from collections import deque
import hashlib

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TecnologiaFocusMonitor:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the focus monitor for tecnología channel"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("focus-bot") or self.get_bot_config("zzz-bot")
        self.target_stream = "desarrollo"  # Canal de tecnología
        self.webhook_url = "http://localhost:5000/webhook"
        
        # Topic tracking
        self.current_topic = None
        self.topic_keywords = set()
        self.conversation_history = deque(maxlen=20)
        self.last_focus_message = None
        self.last_message_time = None
        
        # Technology keywords for topic detection
        self.tech_keywords = {
            'programación', 'codigo', 'software', 'desarrollo', 'api', 'base de datos',
            'frontend', 'backend', 'javascript', 'python', 'java', 'react', 'vue',
            'docker', 'kubernetes', 'aws', 'azure', 'cloud', 'devops', 'git',
            'algoritmo', 'framework', 'libreria', 'bug', 'debug', 'test', 'deploy',
            'servidor', 'cliente', 'microservicios', 'arquitectura', 'seguridad',
            'performance', 'optimización', 'escalabilidad', 'integración'
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
    
    def extract_topic_keywords(self, message: str) -> set:
        """Extract keywords from message to identify the main topic"""
        # Convert to lowercase and remove punctuation
        cleaned = re.sub(r'[^\w\s]', ' ', message.lower())
        words = cleaned.split()
        
        # Filter technology keywords
        tech_words = {word for word in words if word in self.tech_keywords}
        
        # Also extract potential proper nouns (capitalized words)
        proper_nouns = {word for word in words if word.istitle() and len(word) > 3}
        
        return tech_words.union(proper_nouns)
    
    def calculate_topic_similarity(self, keywords1: set, keywords2: set) -> float:
        """Calculate similarity between two sets of keywords"""
        if not keywords1 or not keywords2:
            return 0.0
        
        intersection = keywords1.intersection(keywords2)
        union = keywords1.union(keywords2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def detect_topic_change(self, message: str) -> bool:
        """Detect if the message represents a topic change"""
        current_keywords = self.extract_topic_keywords(message)
        
        # If we don't have a current topic, establish one
        if not self.current_topic or not self.topic_keywords:
            self.current_topic = self.extract_topic_summary(message)
            self.topic_keywords = current_keywords
            logger.info(f"New topic established: {self.current_topic}")
            return False
        
        # Calculate similarity with current topic
        similarity = self.calculate_topic_similarity(current_keywords, self.topic_keywords)
        
        # Consider it a topic change if similarity is low (< 0.3)
        if similarity < 0.3 and current_keywords:
            logger.info(f"Topic change detected! Similarity: {similarity:.2f}")
            logger.info(f"Previous topic keywords: {self.topic_keywords}")
            logger.info(f"New keywords: {current_keywords}")
            return True
        
        return False
    
    def extract_topic_summary(self, message: str) -> str:
        """Extract a brief summary of the topic from message"""
        # Simple extraction: take first few words and main tech keywords
        words = message.split()[:8]
        tech_words = [word for word in words if word.lower() in self.tech_keywords]
        
        if tech_words:
            return f"Discusión sobre {', '.join(tech_words[:3])}"
        
        return " ".join(words[:5]) + "..."
    
    def get_recent_messages(self, limit: int = 10) -> List[Dict]:
        """Get recent messages from the desarrollo stream"""
        try:
            server_url = "http://localhost"
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
            
            response = requests.get(url, headers=headers, params=params)
            
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
    
    def send_focus_message(self, original_topic: str, new_topic: str) -> bool:
        """Send a focus reminder message via webhook"""
        try:
            message_content = f"""**@all Recordemos el foco de la conversación** :point_up:

**Tema original:** {original_topic}
**Nueva dirección:** {new_topic}

Para mantener la conversación organizada y productiva, sugiero:
1. Si es un tema relacionado, continuemos en el mismo hilo
2. Si es un tema diferente, consideren abrir un nuevo topic
3. Si necesiten discutir varios temas, usen threads separados

**Canal:** #{self.target_stream} | **Timestamp:** {datetime.now().strftime('%H:%M')}

---
*Mensaje automático del monitor de foco - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            payload = {
                "message": message_content,
                "stream": self.target_stream,
                "topic": "recordatorio-foco",
                "type": "focus_reminder"
            }
            
            response = requests.post(self.webhook_url, json=payload)
            
            if response.status_code == 200:
                logger.info("Focus reminder sent successfully")
                self.last_focus_message = datetime.now()
                return True
            else:
                logger.error(f"Error sending focus message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending focus message: {e}")
            return False
    
    def send_message_via_api(self, content: str, topic: str = "recordatorio-foco") -> bool:
        """Send message directly via Zulip API"""
        try:
            server_url = "http://localhost"
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
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info("Message sent via API successfully")
                return True
            else:
                logger.error(f"Error sending message via API: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message via API: {e}")
            return False
    
    def should_send_focus_reminder(self) -> bool:
        """Determine if we should send a focus reminder"""
        if not self.last_focus_message:
            return True
        
        # Wait at least 10 minutes between reminders
        time_since_last = datetime.now() - self.last_focus_message
        return time_since_last > timedelta(minutes=10)
    
    def monitor_conversation(self):
        """Main monitoring loop"""
        logger.info(f"Starting conversation monitoring for #{self.target_stream}")
        
        while True:
            try:
                # Get recent messages
                messages = self.get_recent_messages(limit=5)
                
                if messages:
                    # Process the most recent message
                    latest_message = messages[-1]
                    message_content = latest_message.get("content", "")
                    sender = latest_message.get("sender_full_name", "Unknown")
                    
                    # Skip bot messages
                    if "bot" in sender.lower():
                        time.sleep(30)
                        continue
                    
                    logger.info(f"Processing message from {sender}: {message_content[:100]}...")
                    
                    # Check for topic change
                    if self.detect_topic_change(message_content):
                        new_topic = self.extract_topic_summary(message_content)
                        
                        if self.should_send_focus_reminder():
                            logger.info(f"Sending focus reminder: {self.current_topic} -> {new_topic}")
                            
                            focus_message = f"""**@all Mantengamos el foco en la conversación** :light_bulb:

**Tema actual:** {self.current_topic}
**Nueva dirección detectada:** {new_topic}

Para mejor organización:
- Si es relacionado, continuemos aquí
- Si es diferente, consideren un nuevo topic
- Para temas variados, usen threads separados

*Monitor de #{self.target_stream} - {datetime.now().strftime('%H:%M')}*
"""
                            
                            # Try webhook first, fallback to API
                            if not self.send_focus_message(self.current_topic, new_topic):
                                self.send_message_via_api(focus_message)
                            
                            # Update current topic
                            self.current_topic = new_topic
                            self.topic_keywords = self.extract_topic_keywords(message_content)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(30)  # Wait before retrying
    
    def test_monitor(self):
        """Test the monitor with sample messages"""
        logger.info("Testing focus monitor...")
        
        test_messages = [
            "Estoy trabajando en una nueva API REST con Python y FastAPI",
            "Alguien sabe cómo optimizar queries en PostgreSQL?",
            "Por cierto, ¿qué opinan de las nuevas políticas de la empresa?",
            "Volviendo al tema, necesito ayuda con Docker para mi aplicación",
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
                self.topic_keywords = self.extract_topic_keywords(message)
            else:
                logger.info("  -> Same topic, no action needed")
            
            print()

def main():
    """Main function"""
    monitor = TecnologiaFocusMonitor()
    
    try:
        print("="*60)
        print("TECNOLOGÍA FOCUS MONITOR")
        print("="*60)
        print(f"Monitoring channel: #{monitor.target_stream}")
        print(f"Focus reminder interval: 10 minutes")
        print("="*60)
        
        # Test first
        print("\nRunning tests...")
        monitor.test_monitor()
        
        # Ask user if they want to start monitoring
        response = input("\nStart real-time monitoring? (y/n): ").lower()
        if response == 'y':
            print("\nStarting monitoring... (Ctrl+C to stop)")
            monitor.monitor_conversation()
        else:
            print("Monitoring not started.")
            
    except KeyboardInterrupt:
        logger.info("Monitor stopped by user")
    except Exception as e:
        logger.error(f"Monitor error: {e}")

if __name__ == "__main__":
    main()
