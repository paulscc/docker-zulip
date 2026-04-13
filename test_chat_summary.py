#!/usr/bin/env python3
"""
Test script for chat summary processor
"""

import requests
import json
from datetime import datetime

def test_zulip_connection():
    """Test connection to Zulip API"""
    
    # Load bot config
    try:
        with open("bot_config.json", 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    # Get bot config
    bot = None
    for b in config.get("bots", []):
        if b.get("bot_name") == "xxx-bot":
            bot = b
            break
    
    if not bot:
        print("Bot xxx-bot not found in config")
        return
    
    print(f"Testing connection to: {bot['server_url']}")
    print(f"Bot email: {bot.get('email', 'N/A')}")
    
    # Test API connection
    try:
        url = f"{bot['server_url']}/api/v1/messages"
        headers = {
            "Authorization": f"Bearer {bot['api_key']}",
            "Content-Type": "application/json"
        }
        
        params = {
            "stream": "general",
            "topic": "chat",
            "num_before": 5,
            "num_after": 0,
            "narrow": json.dumps([
                {"operator": "stream", "operand": "general"},
                {"operator": "topic", "operand": "chat"}
            ])
        }
        
        response = requests.get(url, headers=headers, params=params, verify=False, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            messages = response.json().get("messages", [])
            print(f"Found {len(messages)} messages")
            
            for i, msg in enumerate(messages[:3]):
                print(f"\nMessage {i+1}:")
                print(f"  Sender: {msg.get('sender_full_name', 'N/A')}")
                print(f"  Content: {msg.get('content', '')[:50]}...")
                print(f"  Timestamp: {msg.get('timestamp', 'N/A')}")
        else:
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def send_test_messages():
    """Send test messages to Zulip"""
    
    try:
        with open("bot_config.json", 'r') as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        return
    
    # Find a working bot
    bot = None
    for b in config.get("bots", []):
        if b.get("bot_name") == "nnnnn-bot":
            bot = b
            break
    
    if not bot:
        print("No working bot found")
        return
    
    messages = [
        "Este es un mensaje de prueba para el sistema de resúmenes de chat",
        "El sistema genera resúmenes cada 1 minuto de los mensajes recientes",
        "Los resúmenes incluyen enlaces directos a los mensajes originales",
        "Esta es una prueba para verificar que el flujo completo funcione correctamente",
        "Los resúmenes se publican en Kafka topic zulip-summaries"
    ]
    
    url = f"{bot['server_url']}/api/v1/messages"
    headers = {
        "Authorization": f"Bearer {bot['api_key']}",
        "Content-Type": "application/json"
    }
    
    for i, content in enumerate(messages):
        payload = {
            "type": "stream",
            "to": "general",
            "topic": "chat",
            "content": f"{content}\n\n*Mensaje de prueba #{i+1} - {datetime.now().strftime('%H:%M:%S')}*"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, verify=False, timeout=30)
            
            if response.status_code == 200:
                print(f"Message {i+1} sent successfully")
            else:
                print(f"Error sending message {i+1}: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Error sending message {i+1}: {e}")
        
        import time
        time.sleep(1)

if __name__ == "__main__":
    print("=== Testing Zulip Connection ===")
    test_zulip_connection()
    
    print("\n=== Sending Test Messages ===")
    send_test_messages()
    
    print("\n=== Test Complete ===")
    print("Check the chat_summary_processor.py output for summaries")
