#!/usr/bin/env python3
"""
Setup Zulip Channels
Create 4 channels: comercio, desarrollo, equipo, general
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ZulipChannelSetup:
    def __init__(self, config_file: str = "bot_config.json"):
        """Initialize Zulip channel setup"""
        self.config = self.load_config(config_file)
        self.incoming_bot = self.get_bot_config("zzz-bot")
        self.channels = [
            {
                "name": "comercio",
                "description": "Canal para discusiones sobre comercio, ventas y negocios"
            },
            {
                "name": "desarrollo", 
                "description": "Canal para desarrollo de software, programación y tecnología"
            },
            {
                "name": "equipo",
                "description": "Canal para comunicación del equipo, colaboraciones y coordinación"
            },
            {
                "name": "general",
                "description": "Canal general para conversaciones variadas y anuncios"
            }
        ]
        
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
    
    def create_stream(self, stream_name: str, description: str) -> bool:
        """Create a stream in Zulip"""
        try:
            server_url = "http://localhost"
            url = f"{server_url}/api/v1/streams"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "name": stream_name,
                "description": description,
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
            server_url = "http://localhost"
            url = f"{server_url}/api/v1/users/me/subscriptions"
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
    
    def send_welcome_message(self, stream_name: str) -> bool:
        """Send welcome message to stream"""
        try:
            server_url = "http://localhost"
            url = f"{server_url}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            welcome_content = f"""**Bienvenidos al canal #{stream_name}!** :wave:

Este es el canal oficial para {self.get_channel_description(stream_name)}.

**Características del canal:**
- Resúmenes automáticos con IA cuando hay muchos mensajes
- Monitoreo por bots inteligentes
- Integración con Kafka para procesamiento eficiente

**Para probar el sistema:**
1. Envía varios mensajes en este canal
2. Cuando haya 10+ mensajes no leídos, se generará un resumen automático
3. El resumen aparecerá en `#{stream_name}/resumen-general`

**Comandos útiles:**
- @mention a los bots para asistencia
- Usa topics específicos para mejor organización

---
*Canal configurado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            payload = {
                "type": "stream",
                "to": stream_name,
                "topic": "bienvenida",
                "content": welcome_content
            }
            
            response = requests.post(url, headers=headers, json=payload)
            
            if response.status_code == 200:
                logger.info(f"Welcome message sent to '{stream_name}'")
                return True
            else:
                logger.error(f"Error sending welcome message: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome message: {e}")
            return False
    
    def get_channel_description(self, stream_name: str) -> str:
        """Get description for a channel"""
        for channel in self.channels:
            if channel["name"] == stream_name:
                return channel["description"]
        return "discusiones variadas"
    
    def setup_all_channels(self) -> bool:
        """Setup all channels"""
        logger.info("Setting up Zulip channels...")
        
        # Test bot connection
        try:
            server_url = "http://localhost"
            url = f"{server_url}/api/v1/users/me"
            headers = {
                "Authorization": f"Bearer {self.incoming_bot['api_key']}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, verify=False)
            if response.status_code != 200:
                logger.error("Bot connection failed")
                return False
                
            user_data = response.json()
            logger.info(f"Connected as: {user_data.get('full_name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Bot connection error: {e}")
            return False
        
        # Create channels
        success = True
        for channel in self.channels:
            stream_name = channel["name"]
            description = channel["description"]
            
            logger.info(f"Processing channel: {stream_name}")
            
            # Create stream
            if not self.create_stream(stream_name, description):
                success = False
                continue
            
            # Subscribe to stream
            if not self.subscribe_to_stream(stream_name):
                success = False
                continue
            
            # Send welcome message
            if not self.send_welcome_message(stream_name):
                success = False
                continue
        
        return success

def main():
    """Main function to setup Zulip channels"""
    setup = ZulipChannelSetup()
    
    try:
        print("="*60)
        print("ZULIP CHANNELS SETUP")
        print("="*60)
        
        success = setup.setup_all_channels()
        
        if success:
            print("\n" + "="*60)
            print("ZULIP CHANNELS SETUP COMPLETED!")
            print("="*60)
            print("\nChannels created:")
            for channel in setup.channels:
                print(f"- #{channel['name']}: {channel['description']}")
            
            print("\nNext steps:")
            print("1. Update bot configuration to monitor these channels")
            print("2. Start the Kafka webhook system")
            print("3. Test by sending messages to the channels")
            print("4. Check for automatic summaries")
            print("="*60)
        else:
            print("\n" + "="*60)
            print("ZULIP CHANNELS SETUP FAILED!")
            print("Please check the logs above for details")
            print("="*60)
            
    except KeyboardInterrupt:
        logger.info("Setup interrupted by user")
    except Exception as e:
        logger.error(f"Setup error: {e}")

if __name__ == "__main__":
    main()
