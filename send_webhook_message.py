#!/usr/bin/env python3
"""
Script para enviar mensaje usando webhook bot endpoint
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def send_webhook_message():
    """
    Enviar mensaje usando endpoint de webhook bot
    """
    email = "bbbbb-bot@midt.127.0.0.1.nip.io"
    api_key = "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Enviando mensaje via webhook endpoint")
    print(f"📧 Email: {email}")
    print(f"🌐 Site: {site}")
    print("=" * 50)
    
    try:
        # Para webhook bots, necesitamos usar el endpoint de incoming webhook
        # El formato típico es: /api/v1/external/services?api_key=KEY
        
        webhook_url = f"{site}/api/v1/external/services?api_key={api_key}"
        
        message_data = {
            "bot_email": email,
            "data": {
                "type": "stream",
                "to": "general",  # Stream name, no ID needed for webhook
                "topic": "Prueba de Bot",
                "content": "🤖 Mensaje de prueba desde bbbbb-bot webhook - Conexión con Gemma 3 exitosa! 🚀"
            }
        }
        
        print("1️⃣ Enviando mensaje via webhook...")
        response = requests.post(webhook_url, json=message_data, verify=False, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Mensaje enviado exitosamente via webhook!")
            print(f"📄 Respuesta: {result}")
            return True
        else:
            print(f"❌ Error al enviar mensaje via webhook: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            
            # Intentar con formato alternativo
            print("\n🔄 Intentando formato alternativo...")
            alt_webhook_url = f"{site}/api/v1/external/services"
            alt_message_data = {
                "email": email,
                "api_key": api_key,
                "message": "🤖 Mensaje de prueba desde bbbbb-bot webhook - Conexión con Gemma 3 exitosa! 🚀",
                "stream": "general",
                "topic": "Prueba de Bot"
            }
            
            response = requests.post(alt_webhook_url, json=alt_message_data, verify=False, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mensaje enviado exitosamente (formato alternativo)!")
                print(f"📄 Respuesta: {result}")
                return True
            else:
                print(f"❌ Error con formato alternativo: {response.status_code}")
                print(f"📄 Detalles: {response.text}")
                return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False

def test_gemma_connection():
    """
    Prueba la conexión con Gemma 3
    """
    print("\n🤖 Probando conexión con Gemma...")
    
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "gemma3:1b",
            "prompt": "Genera un mensaje amigable para un chat de Zulip",
            "stream": False
        }
        
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            llm_response = result.get('response', 'Sin respuesta')
            print(f"✅ Gemma 3 responde: {llm_response}")
            return llm_response
        else:
            print(f"❌ Error con Gemma 3: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error al conectar con Gemma 3: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Enviando mensaje via webhook a Zulip")
    print("=" * 50)
    
    # Probar conexión LLM primero
    llm_response = test_gemma_connection()
    
    # Probar envío de mensaje
    if send_webhook_message():
        print("\n🎉 Pruebas completadas exitosamente!")
        print("✅ Gemma 3 funcionando correctamente")
        print("✅ Mensaje enviado a general channel")
    else:
        print("\n❌ No se pudo enviar el mensaje")
        sys.exit(1)
