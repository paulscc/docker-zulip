#!/usr/bin/env python3
"""
Simple Channel Creation for Zulip
Create 4 channels: comercio, desarrollo, equipo, general
"""

import requests
import json
import logging
from datetime import datetime
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_zulip_channels():
    """Create channels in Zulip"""
    
    # Bot configuration (using zzz-bot)
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "http://localhost"
    
    channels = [
        {"name": "comercio", "description": "Canal para discusiones sobre comercio, ventas y negocios"},
        {"name": "desarrollo", "description": "Canal para desarrollo de software, programación y tecnología"},
        {"name": "equipo", "description": "Canal para comunicación del equipo, colaboraciones y coordinación"},
        {"name": "general", "description": "Canal general para conversaciones variadas y anuncios"}
    ]
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Test connection
    try:
        response = requests.get(f"{server_url}/api/v1/users/me", headers=headers, verify=False)
        if response.status_code == 200:
            user = response.json()
            logger.info(f"Connected as: {user.get('full_name', 'Unknown')}")
        else:
            logger.error(f"Connection failed: {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"Connection error: {e}")
        return False
    
    # Create each channel
    for channel in channels:
        logger.info(f"Creating channel: {channel['name']}")
        
        # Create stream
        stream_payload = {
            "name": channel["name"],
            "description": channel["description"],
            "invite_only": False,
            "stream_post_policy": 1,
            "history_public_to_subscribers": True
        }
        
        try:
            response = requests.post(
                f"{server_url}/api/v1/streams",
                headers=headers,
                json=stream_payload,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"Stream '{channel['name']}' created successfully")
            elif response.status_code == 400 and "already exists" in response.text.lower():
                logger.info(f"Stream '{channel['name']}' already exists")
            else:
                logger.error(f"Error creating stream '{channel['name']}': {response.status_code}")
                continue
            
            # Subscribe to stream
            sub_payload = {
                "subscriptions": [{"name": channel["name"]}]
            }
            
            response = requests.post(
                f"{server_url}/api/v1/users/me/subscriptions",
                headers=headers,
                json=sub_payload,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"Subscribed to '{channel['name']}'")
            else:
                logger.error(f"Error subscribing to '{channel['name']}': {response.status_code}")
                continue
            
            # Send welcome message
            welcome_content = f"""**Bienvenidos al canal #{channel['name']}!** :wave:

Este es el canal oficial para {channel['description']}.

**Características del canal:**
- Resúmenes automáticos con IA cuando hay muchos mensajes
- Monitoreo por bots inteligentes
- Integración con Kafka para procesamiento eficiente

**Para probar el sistema:**
1. Envía varios mensajes en este canal
2. Cuando haya 10+ mensajes no leídos, se generará un resumen automático
3. El resumen aparecerá en `#{channel['name']}/resumen-general`

---
*Canal configurado automáticamente - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""
            
            message_payload = {
                "type": "stream",
                "to": channel["name"],
                "topic": "bienvenida",
                "content": welcome_content
            }
            
            response = requests.post(
                f"{server_url}/api/v1/messages",
                headers=headers,
                json=message_payload,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"Welcome message sent to '{channel['name']}'")
            else:
                logger.error(f"Error sending welcome message: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error processing channel '{channel['name']}': {e}")
            continue
    
    logger.info("Channel creation process completed")
    return True

if __name__ == "__main__":
    print("="*60)
    print("CREATING ZULIP CHANNELS")
    print("="*60)
    
    success = create_zulip_channels()
    
    if success:
        print("\n" + "="*60)
        print("CHANNELS CREATED SUCCESSFULLY!")
        print("="*60)
        print("\nChannels created:")
        print("- #comercio: Comercio, ventas y negocios")
        print("- #desarrollo: Desarrollo de software y tecnología")
        print("- #equipo: Comunicación del equipo")
        print("- #general: Conversaciones variadas y anuncios")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("CHANNEL CREATION FAILED!")
        print("="*60)
