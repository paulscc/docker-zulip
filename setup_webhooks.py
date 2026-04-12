#!/usr/bin/env python3
"""
Setup Webhooks Configuration
Configure webhook bots in Zulip and create necessary streams/topics
"""

import requests
import json
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookSetup:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize webhook setup"""
        self.config = self.load_config(config_file)
        self.outgoing_bot = self.get_bot_config("xxx-bot")
        self.incoming_bot = self.get_bot_config("zzz-bot")
        
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
    
    def create_stream(self, stream_name: str) -> bool:
        """Create a stream if it doesn't exist"""
        try:
            url = f"{self.incoming_bot['server_url']}/api/v1/streams"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": stream_name,
                "description": f"Stream para webhooks y resúmenes automáticos",
                "invite_only": False,
                "stream_post_policy": 1,  # Any organization member can post
                "history_public_to_subscribers": True
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Stream '{stream_name}' created successfully")
                return True
            elif response.status_code == 400 and "already exists" in response.text.lower():
                logger.info(f"Stream '{stream_name}' already exists")
                return True
            else:
                logger.error(f"Error creating stream '{stream_name}': {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating stream: {e}")
            return False
    
    def subscribe_to_stream(self, stream_name: str) -> bool:
        """Subscribe bot to stream"""
        try:
            url = f"{self.incoming_bot['server_url']}/api/v1/users/me/subscriptions"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "subscriptions": [
                    {
                        "name": stream_name
                    }
                ]
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Subscribed to stream '{stream_name}'")
                return True
            else:
                logger.error(f"Error subscribing to stream '{stream_name}': {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error subscribing to stream: {e}")
            return False
    
    def test_bot_connection(self, bot_name: str, bot_config: Dict) -> bool:
        """Test if bot can connect to Zulip"""
        try:
            url = f"{bot_config['server_url']}/api/v1/users/me"
            headers = {
                "Authorization": f"Bearer {bot_config['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                logger.info(f"Bot '{bot_name}' connected successfully - User: {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                logger.error(f"Bot '{bot_name}' connection failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing bot connection: {e}")
            return False
    
    def setup_webhook_environment(self):
        """Setup the complete webhook environment"""
        logger.info("Setting up webhook environment...")
        
        # Test bot connections
        logger.info("Testing bot connections...")
        outgoing_ok = self.test_bot_connection("xxx-bot", self.outgoing_bot)
        incoming_ok = self.test_bot_connection("zzz-bot", self.incoming_bot)
        
        if not outgoing_ok:
            logger.error("Outgoing webhook bot (xxx-bot) connection failed")
            return False
        
        if not incoming_ok:
            logger.error("Incoming webhook bot (zzz-bot) connection failed")
            return False
        
        # Create necessary streams
        streams_to_create = ["webhooks", "resumenes"]
        
        for stream in streams_to_create:
            logger.info(f"Creating stream: {stream}")
            if self.create_stream(stream):
                self.subscribe_to_stream(stream)
            else:
                logger.error(f"Failed to create stream: {stream}")
                return False
        
        # Send setup confirmation messages
        self.send_setup_confirmation()
        
        logger.info("Webhook environment setup completed successfully!")
        return True
    
    def send_setup_confirmation(self):
        """Send confirmation messages to verify setup"""
        try:
            # Send message to webhooks stream
            url = f"{self.incoming_bot['server_url']}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            confirmation_message = f"""**Sistema de Webhooks Configurado** :white_check_mark:

El sistema de webhooks automáticos ha sido configurado exitosamente:

**Bots Configurados:**
- xxx-bot: Outgoing webhook (detección de triggers)
- zzz-bot: Incoming webhook (publicación de resúmenes)

**Streams Creados:**
- #webhooks: Para mensajes de webhook y pruebas
- #resumenes: Para resúmenes automáticos

**Flujo de Trabajo:**
1. El outgoing webhook detecta mensajes no leídos (umbral: 10 mensajes)
2. Envía los mensajes al servicio externo (puerto 8080)
3. El servicio genera resúmenes con Ollama
4. El incoming webhook publica los resúmenes en el stream correspondiente

**Para probar el sistema:**
1. Inicia el servicio: `python webhook_service.py`
2. Inicia el outgoing webhook: `python outgoing_webhook.py`
3. Envía mensajes a cualquier stream/topic

---
*Configurado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            payload = {
                "type": "stream",
                "to": "webhooks",
                "topic": "configuracion",
                "content": confirmation_message
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info("Setup confirmation message sent successfully")
            else:
                logger.error(f"Error sending setup confirmation: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error sending setup confirmation: {e}")

def main():
    """Main function to setup webhooks"""
    setup = WebhookSetup()
    
    try:
        success = setup.setup_webhook_environment()
        if success:
            print("\n" + "="*50)
            print("WEBHOOK SETUP COMPLETED SUCCESSFULLY!")
            print("="*50)
            print("\nNext steps:")
            print("1. Start the webhook service: python webhook_service.py")
            print("2. Start the outgoing webhook: python outgoing_webhook.py")
            print("3. Test by sending messages to any stream")
            print("\nWebhook service will run on: http://localhost:8080")
            print("="*50)
        else:
            print("\n" + "="*50)
            print("WEBHOOK SETUP FAILED!")
            print("Please check the logs above for details")
            print("="*50)
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup error: {e}")

if __name__ == "__main__":
    main()
