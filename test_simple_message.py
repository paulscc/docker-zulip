#!/usr/bin/env python3
"""
Prueba simple de mensaje sin emojis
"""

import json
import requests
import base64
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuración
email = "ccccc-bot@midt.127.0.0.1.nip.io"
api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
server_url = "https://midt.127.0.0.1.nip.io"

# Autenticación
auth_string = f"{email}:{api_key}"
auth_header = base64.b64encode(auth_string.encode()).decode()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Basic {auth_header}"
}

# Mensaje simple
message_data = {
    "type": "stream",
    "to": "general",
    "topic": "chat",
    "content": "Hola desde bot_amigable - test simple"
}

print("🧪 Enviando mensaje simple...")
print(f"Data: {json.dumps(message_data)}")

try:
    url = f"{server_url}/api/v1/messages"
    response = requests.post(url, json=message_data, headers=headers, verify=False, timeout=10)
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Message ID: {result.get('id')}")
    else:
        print(f"❌ Error: {response.status_code}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
