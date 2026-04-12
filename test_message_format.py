#!/usr/bin/env python3
"""
Script para probar diferentes formatos de mensaje en la API de Zulip
"""

import json
import requests
import base64
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_message_formats():
    """Prueba diferentes formatos de mensaje"""
    
    # Configuración del bot
    email = "ccccc-bot@midt.127.0.0.1.nip.io"
    api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
    server_url = "https://midt.127.0.0.1.nip.io"
    
    auth_string = f"{email}:{api_key}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_header}"
    }
    
    url = f"{server_url}/api/v1/messages"
    
    # Formatos de mensaje a probar
    message_formats = [
        {
            "name": "Formato 1: topic",
            "data": {
                "type": "stream",
                "to": "general",
                "topic": "chat",
                "content": "🤖 Test desde formato 1 - topic"
            }
        },
        {
            "name": "Formato 2: subject",
            "data": {
                "type": "stream",
                "to": "general",
                "subject": "chat",
                "content": "🤖 Test desde formato 2 - subject"
            }
        },
        {
            "name": "Formato 3: stream + to + topic",
            "data": {
                "type": "stream",
                "stream": "general",
                "to": "chat",
                "content": "🤖 Test desde formato 3 - stream+to+topic"
            }
        },
        {
            "name": "Formato 4: solo content y type",
            "data": {
                "type": "stream",
                "content": "🤖 Test desde formato 4 - mínimo"
            }
        }
    ]
    
    print("🧪 Probando diferentes formatos de mensaje")
    print("=" * 60)
    
    for i, format_test in enumerate(message_formats, 1):
        print(f"\n{i}. {format_test['name']}")
        print(f"   Data: {json.dumps(format_test['data'], indent=2)}")
        
        try:
            response = requests.post(url, json=format_test['data'], headers=headers, verify=False, timeout=10)
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ ÉXITO! Message ID: {result.get('id')}")
                return True
            else:
                print(f"   ❌ Error: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
    
    return False

def test_bot_info():
    """Prueba obtener información del bot"""
    print("\n🤖 Verificando información del bot...")
    
    email = "ccccc-bot@midt.127.0.0.1.nip.io"
    api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
    server_url = "https://midt.127.0.0.1.nip.io"
    
    auth_string = f"{email}:{api_key}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_header}"
    }
    
    try:
        url = f"{server_url}/api/v1/users/me"
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Bot autenticado: {data.get('full_name', 'Unknown')}")
            print(f"   📧 Email: {data.get('email', 'Unknown')}")
            print(f"   🆔 ID: {data.get('user_id', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de formato de mensaje")
    print("=" * 60)
    
    if test_bot_info():
        success = test_message_formats()
        
        if success:
            print("\n🎉 Se encontró un formato que funciona!")
        else:
            print("\n❌ Ningún formato funcionó. Revisar documentación de la API.")
    else:
        print("\n❌ No se pudo autenticar el bot.")
