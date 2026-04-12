#!/usr/bin/env python3
"""
LLM Topic Analyzer
Analiza conversaciones usando LLM para detectar cambios de tema
y actualiza automáticamente los topics en Zulip
"""

import requests
import json
import logging
import time
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import deque

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMTopicAnalyzer:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize the LLM topic analyzer"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("xxx-bot")  # Use webhook_outbound bot
        self.target_stream = "desarrollo"
        
        # LLM Configuration (Gemma2 local)
        self.llm_url = "http://localhost:11434/api/generate"
        self.llm_model = "gemma2:2b"
        
        # Topic tracking
        self.current_topics = {}  # topic_name -> topic_info
        self.last_analysis_time = None
        self.last_topic_update = None
        self.analysis_interval = 20  # segundos
        self.min_update_interval = 300  # 5 minutos entre actualizaciones
        
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
    
    def call_llm(self, prompt: str) -> Optional[str]:
        """Call LLM for topic analysis"""
        try:
            payload = {
                "model": self.llm_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 200
                }
            }
            
            response = requests.post(self.llm_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"LLM call failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            return None
    
    def create_topic_analysis_prompt(self, current_topic: str, messages: List[str]) -> str:
        """Create prompt for LLM topic analysis"""
        messages_text = "\n".join([f"- \"{msg}\"" for msg in messages[-5:]])  # Last 5 messages
        
        prompt = f"""El título actual del topic es "{current_topic}".

Aquí están los últimos mensajes:
{messages_text}

¿El tema sigue siendo '{current_topic}' o debería cambiarse?
Si debe cambiarse, sugiere un nuevo título breve (máximo 50 caracteres).

Responde en este formato exacto:
DECISION: [MANTENER/CAMBIAR]
TITULO: [título actual o nuevo título]
RAZON: [breve explicación]

Ejemplos:
DECISION: CAMBIAR
TITULO: Optimización API REST
RAZON: La conversación se centró en optimización de APIs

DECISION: MANTENER
TITULO: Presupuesto Q2
RAZON: Los mensajes siguen relacionados con presupuesto"""
        
        return prompt
    
    def parse_llm_response(self, response: str) -> Tuple[str, str, str]:
        """Parse LLM response to extract decision, title, and reason"""
        decision = "MANTENER"
        title = ""
        reason = ""
        
        try:
            lines = response.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('DECISION:'):
                    decision = line.split(':', 1)[1].strip().upper()
                elif line.startswith('TITULO:'):
                    title = line.split(':', 1)[1].strip()
                elif line.startswith('RAZON:'):
                    reason = line.split(':', 1)[1].strip()
            
            # Clean title (remove quotes, limit length)
            title = re.sub(r'["\']', '', title)
            title = title[:50] if len(title) > 50 else title
            
            return decision, title, reason
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            return "MANTENER", "", "Error parsing response"
    
    def get_recent_messages_by_topic(self, topic_name: str, limit: int = 5) -> List[Dict]:
        """Get recent messages from a specific topic"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            # Get messages from specific topic
            params = {
                "type": "stream",
                "stream": self.target_stream,
                "topic": topic_name,
                "narrow": json.dumps([
                    {"operator": "stream", "operand": self.target_stream},
                    {"operator": "topic", "operand": topic_name}
                ]),
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
                logger.error(f"Error getting messages for topic '{topic_name}': {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting messages for topic '{topic_name}': {e}")
            return []
    
    def get_all_active_topics(self) -> List[Dict]:
        """Get all active topics in the stream"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/streams/{self.target_stream}/topics"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            response = requests.get(url, auth=auth, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("topics", [])
            else:
                logger.error(f"Error getting topics: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting topics: {e}")
            return []
    
    def update_topic_name(self, old_topic: str, new_topic: str) -> bool:
        """Update topic name in Zulip"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages/{old_topic}/update_topic"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            payload = {
                "stream_id": self.get_stream_id(),
                "topic": old_topic,
                "new_topic": new_topic
            }
            
            response = requests.patch(url, auth=auth, json=payload, verify=False)
            
            if response.status_code == 200:
                logger.info(f"Topic updated: '{old_topic}' -> '{new_topic}'")
                return True
            else:
                logger.error(f"Error updating topic: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error updating topic: {e}")
            return False
    
    def get_stream_id(self) -> int:
        """Get stream ID for the target stream"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/streams"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            response = requests.get(url, auth=auth, verify=False)
            
            if response.status_code == 200:
                data = response.json()
                streams = data.get("streams", [])
                
                for stream in streams:
                    if stream.get("name") == self.target_stream:
                        return stream.get("stream_id", 0)
                
        except Exception as e:
            logger.error(f"Error getting stream ID: {e}")
        
        return 0
    
    def analyze_topic_changes(self):
        """Analyze topic changes using LLM"""
        logger.info("Running LLM topic analysis...")
        
        # Get all active topics
        topics = self.get_all_active_topics()
        
        if not topics:
            logger.info("No active topics found")
            return
        
        for topic_info in topics:
            topic_name = topic_info.get("name", "")
            
            if not topic_name:
                continue
            
            # Skip if recently updated
            if topic_name in self.current_topics:
                last_update = self.current_topics[topic_name].get("last_update")
                if last_update and (datetime.now() - last_update).total_seconds() < self.min_update_interval:
                    continue
            
            # Get recent messages for this topic
            messages = self.get_recent_messages_by_topic(topic_name, limit=5)
            
            if not messages:
                continue
            
            # Skip if all messages are from bots
            human_messages = [msg for msg in messages if "bot" not in msg.get("sender_full_name", "").lower()]
            if len(human_messages) < 2:  # Need at least 2 human messages
                continue
            
            # Extract message content
            message_contents = [msg.get("content", "") for msg in human_messages]
            
            # Create LLM prompt
            prompt = self.create_topic_analysis_prompt(topic_name, message_contents)
            
            # Call LLM
            llm_response = self.call_llm(prompt)
            
            if not llm_response:
                continue
            
            # Parse LLM response
            decision, new_title, reason = self.parse_llm_response(llm_response)
            
            logger.info(f"Topic '{topic_name}': {decision} - {reason}")
            
            # Update topic if needed
            if decision == "CAMBIAR" and new_title and new_title != topic_name:
                logger.info(f"Updating topic: '{topic_name}' -> '{new_title}'")
                
                if self.update_topic_name(topic_name, new_title):
                    # Update tracking
                    self.current_topics[new_title] = {
                        "original_topic": topic_name,
                        "last_update": datetime.now(),
                        "reason": reason
                    }
                    
                    # Send notification about topic change
                    self.send_topic_change_notification(topic_name, new_title, reason)
            
            # Update tracking
            self.current_topics[topic_name] = {
                "last_analysis": datetime.now(),
                "last_update": self.current_topics.get(topic_name, {}).get("last_update"),
                "decision": decision,
                "reason": reason
            }
    
    def send_topic_change_notification(self, old_topic: str, new_topic: str, reason: str):
        """Send notification about topic change"""
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            notification = f"""**Topic Actualizado Automáticamente** :robot:

**Topic anterior:** {old_topic}
**Nuevo topic:** {new_topic}
**Razón:** {reason}

*Actualizado por LLM Topic Analyzer - {datetime.now().strftime('%H:%M:%S')}*"""
            
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": new_topic,
                "content": notification
            }
            
            response = requests.post(url, auth=auth, data=payload, verify=False)
            
            if response.status_code == 200:
                logger.info("Topic change notification sent")
            else:
                logger.error(f"Error sending notification: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending topic change notification: {e}")
    
    def should_analyze(self) -> bool:
        """Check if we should run analysis"""
        if not self.last_analysis_time:
            return True
        
        time_since_last = datetime.now() - self.last_analysis_time
        return time_since_last.total_seconds() >= self.analysis_interval
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        logger.info(f"Starting LLM topic analysis for #{self.target_stream}")
        logger.info(f"Analysis interval: {self.analysis_interval} seconds")
        logger.info(f"LLM model: {self.llm_model}")
        
        while True:
            try:
                if self.should_analyze():
                    self.analyze_topic_changes()
                    self.last_analysis_time = datetime.now()
                
                time.sleep(self.analysis_interval)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                time.sleep(10)  # Wait before retrying
    
    def test_analyzer(self):
        """Test the LLM topic analyzer"""
        logger.info("Testing LLM topic analyzer...")
        
        # Test LLM connection
        test_prompt = "Responde con 'OK' si puedes leer esto."
        response = self.call_llm(test_prompt)
        
        if not response or "OK" not in response:
            logger.error("LLM test failed")
            return False
        
        logger.info("LLM connection test: OK")
        
        # Test topic analysis
        test_messages = [
            "Estoy trabajando en una API REST con Python",
            "Necesito optimizar las consultas a la base de datos",
            "Alguien sabe cómo mejorar el rendimiento del frontend?"
        ]
        
        prompt = self.create_topic_analysis_prompt("API Development", test_messages)
        llm_response = self.call_llm(prompt)
        
        if llm_response:
            decision, title, reason = self.parse_llm_response(llm_response)
            print(f"\nTest Analysis:")
            print(f"Decision: {decision}")
            print(f"Title: {title}")
            print(f"Reason: {reason}")
            print(f"LLM Response: {llm_response}")
        
        return True

def main():
    """Main function"""
    analyzer = LLMTopicAnalyzer()
    
    try:
        print("="*60)
        print("LLM TOPIC ANALYZER")
        print("="*60)
        print(f"Target channel: #{analyzer.target_stream}")
        print(f"Analysis interval: {analyzer.analysis_interval} seconds")
        print(f"LLM model: {analyzer.llm_model}")
        print("Features:")
        print("  - Analyzes topics using LLM every 20 seconds")
        print("  - Detects when conversation drifts from topic title")
        print("  - Automatically updates topic names")
        print("  - Sends notifications about topic changes")
        print("="*60)
        
        # Test first
        print("\nRunning LLM test...")
        if not analyzer.test_analyzer():
            print("LLM test failed. Please check Ollama is running.")
            return
        
        # Ask user if they want to start monitoring
        response = input("\nStart real-time monitoring? (y/n): ").lower()
        if response == 'y':
            print("\nStarting LLM topic monitoring... (Ctrl+C to stop)")
            analyzer.start_monitoring()
        else:
            print("Monitoring not started.")
            
    except KeyboardInterrupt:
        logger.info("Analyzer stopped by user")
    except Exception as e:
        logger.error(f"Analyzer error: {e}")

if __name__ == "__main__":
    main()
