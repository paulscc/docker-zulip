#!/usr/bin/env python3
"""
Script para probar bot webhook y enviar mensaje usando webhook URL
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_webhook_bot():
    """
    Prueba enviar mensaje usando webhook bot
    """
    email = "bbbbb-bot@midt.127.0.0.1.nip.io"
    api_key = "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Probando webhook bot bbbbb-bot")
    print(f"📧 Email: {email}")
    print(f"🌐 Site: {site}")
    print("=" * 50)
    
    try:
        # Para webhook bots, necesitamos usar endpoint diferente
        # Primero intentemos obtener streams públicos
        print("1️⃣ Obteniendo streams públicos...")
        response = requests.get(f"{site}/api/v1/streams", verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            print("📋 Streams públicos disponibles:")
            general_stream = None
            for stream in streams.get('streams', []):
                stream_name = stream.get('name', 'Desconocido')
                stream_id = stream.get('stream_id', 'N/A')
                print(f"  - {stream_name} (ID: {stream_id})")
                
                if stream_name.lower() == 'general':
                    general_stream = stream
        else:
            print(f"❌ Error al obtener streams: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
        # Para webhook bots, necesitamos usar un endpoint diferente
        # Intentemos con el endpoint de mensajes para webhook bots
        if general_stream:
            print(f"\n2️⃣ Enviando mensaje al stream 'general' via webhook...")
            
            # Webhook bots usan un endpoint diferente
            webhook_url = f"{site}/api/v1/external/services"
            
            # O intentamos con el endpoint normal pero sin autenticación
            # ya que webhook bots no usan auth básica
            message_data = {
                "bot_email": email,
                "api_key": api_key,
                "data": {
                    "type": "stream",
                    "to": general_stream['stream_id'], 
                    "topic": "Prueba de Bot",
                    "content": "🤖 Mensaje de prueba desde bbbbb-bot webhook - Conexión con Gemma 3 exitosa! 🚀"
                }
            }
            
            response = requests.post(webhook_url, json=message_data, verify=False, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mensaje enviado exitosamente via webhook!")
                print(f"📄 Respuesta: {result}")
                return True
            else:
                print(f"❌ Error al enviar mensaje via webhook: {response.status_code}")
                print(f"📄 Detalles: {response.text}")
                
                # Intentemos con el endpoint normal
                print("\n🔄 Intentando con endpoint normal...")
                normal_url = f"{site}/api/v1/messages"
                normal_data = {
                    "type": "stream",
                    "to": general_stream['stream_id'],
                    "topic": "Prueba de Bot", 
                    "content": "🤖 Mensaje de prueba desde bbbbb-bot - Conexión con Gemma 3 exitosa! 🚀"
                }
                
                response = requests.post(normal_url, json=normal_data, verify=False, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Mensaje enviado exitosamente!")
                    print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Error con endpoint normal: {response.status_code}")
                    print(f"📄 Detalles: {response.text}")
                    return False
        else:
            print("❌ No se encontró el stream 'general'")
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
    print("🚀 Iniciando pruebas para webhook bot bbbbb-bot")
    print("=" * 50)
    
    # Probar conexión LLM primero
    llm_response = test_gemma_connection()
    
    # Probar conexión del bot webhook
    if test_webhook_bot():
        print("\n🎉 Pruebas del webhook bot exitosas!")
        if llm_response:
            print(f"🤖 Gemma 3 funcionando correctamente")
    else:
        print("\n❌ Hubo errores en las pruebas del webhook bot")
        sys.exit(1)
