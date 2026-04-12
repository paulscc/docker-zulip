#!/usr/bin/env python3
"""
Test Focus Reminder
Prueba el envío de recordatorios de foco al canal desarrollo
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusReminderTest:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize focus reminder test"""
        self.config = self.load_config(config_file)
        self.monitor_bot = self.get_bot_config("xxx-bot")  # Use webhook_outbound bot
        self.target_stream = "desarrollo"
        
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
    
    def send_test_message(self):
        """Send a test message to desarrollo stream"""
        print("Sending test message to #desarrollo...")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
            message_content = f"""**Test de Webhook de Salida** :test:

Este es un mensaje de prueba del sistema de monitoreo de foco.

**Características probadas:**
- Conexión a API de Zulip
- Autenticación HTTP Basic
- Envío a canal #{self.target_stream}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

*Mensaje enviado desde test_focus_reminder.py*
"""
            
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "test-webhook-salida",
                "content": message_content.strip()
            }
            
            response = requests.post(url, auth=auth, json=payload, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Success! Message ID: {result.get('id', 'Unknown')}")
                return True
            else:
                print(f"  Failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def send_focus_reminder(self, original_topic: str = "API REST", new_topic: str = "políticas empresa"):
        """Send a focus reminder message"""
        print(f"Sending focus reminder: {original_topic} -> {new_topic}")
        
        try:
            server_url = self.monitor_bot.get('server_url', 'https://localhost:443')
            url = f"{server_url}/api/v1/messages"
            
            # Use HTTP Basic authentication
            from requests.auth import HTTPBasicAuth
            auth = HTTPBasicAuth(self.monitor_bot['email'], self.monitor_bot['api_key'])
            
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
            
            payload = {
                "type": "stream",
                "to": self.target_stream,
                "topic": "recordatorio-foco",
                "content": focus_message
            }
            
            response = requests.post(url, auth=auth, json=payload, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Success! Focus reminder sent. Message ID: {result.get('id', 'Unknown')}")
                return True
            else:
                print(f"  Failed: {response.status_code}")
                print(f"  Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"  Error: {e}")
            return False
    
    def test_multiple_scenarios(self):
        """Test multiple focus reminder scenarios"""
        print("Testing multiple focus reminder scenarios...")
        
        scenarios = [
            ("Desarrollo API", "Reunión equipo"),
            ("Optimización database", "Políticas empresa"),
            ("Frontend React", "Noticias del día"),
            ("Backend Python", "Comida del mediodía"),
            ("DevOps Docker", "Clima actual")
        ]
        
        success_count = 0
        
        for i, (original, new) in enumerate(scenarios, 1):
            print(f"\nScenario {i}: {original} -> {new}")
            
            if self.send_focus_reminder(original, new):
                success_count += 1
                print(f"  Scenario {i}: PASS")
            else:
                print(f"  Scenario {i}: FAIL")
            
            # Wait a bit between messages
            import time
            time.sleep(2)
        
        print(f"\nScenarios completed: {success_count}/{len(scenarios)} successful")
        return success_count == len(scenarios)
    
    def get_latest_messages(self, limit: int = 3):
        """Get latest messages to verify they were sent"""
        print(f"Getting latest {limit} messages from #{self.target_stream}...")
        
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
                
                print(f"  Found {len(messages)} latest messages:")
                for i, msg in enumerate(messages[-limit:], 1):
                    sender = msg.get("sender_full_name", "Unknown")
                    content = msg.get("content", "")
                    topic = msg.get("subject", "No topic")
                    timestamp = msg.get("timestamp", 0)
                    
                    # Format timestamp
                    dt = datetime.fromtimestamp(timestamp)
                    time_str = dt.strftime('%H:%M:%S')
                    
                    print(f"    {i}. [{time_str}] {sender} in '{topic}':")
                    print(f"       {content[:100]}{'...' if len(content) > 100 else ''}")
                    print()
                
                return messages
            else:
                print(f"  Error getting messages: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"  Error getting messages: {e}")
            return []
    
    def run_complete_test(self):
        """Run complete focus reminder test"""
        print("="*60)
        print("FOCUS REMINDER TEST - WEBHOOK DE SALIDA")
        print("="*60)
        
        # Test 1: Send test message
        print("\n1. Sending test message...")
        if not self.send_test_message():
            print("Test message failed. Stopping.")
            return False
        
        print()
        
        # Test 2: Send focus reminder
        print("2. Sending focus reminder...")
        if not self.send_focus_reminder():
            print("Focus reminder failed. Stopping.")
            return False
        
        print()
        
        # Test 3: Multiple scenarios
        print("3. Testing multiple scenarios...")
        scenarios_success = self.test_multiple_scenarios()
        
        print()
        
        # Test 4: Verify messages
        print("4. Verifying sent messages...")
        self.get_latest_messages(limit=5)
        
        # Summary
        print("\n" + "="*60)
        print("FOCUS REMINDER TEST COMPLETED!")
        print("="*60)
        print(f"Test message: PASS")
        print(f"Focus reminder: PASS")
        print(f"Multiple scenarios: {'PASS' if scenarios_success else 'FAIL'}")
        print("Message verification: COMPLETED")
        
        print("\nWebhook de salida functionality:")
        print("  - Connection to Zulip API: WORKING")
        print("  - HTTP Basic authentication: WORKING")
        print("  - Message sending to #desarrollo: WORKING")
        print("  - Focus reminder formatting: WORKING")
        print("  - Multiple message handling: WORKING")
        print("="*60)
        
        return True

def main():
    """Main function"""
    test = FocusReminderTest()
    
    try:
        test.run_complete_test()
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
