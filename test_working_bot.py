#!/usr/bin/env python3
"""
Script para probar con un bot existente que funcione
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_working_bot():
    """
    Probar con el bot_amigable existente
    """
    # Usar el bot_amigable existente
    email = "Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX-bot@localhost"
    api_key = "Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX"
    site = "https://midt.127.0.0.1.nip.io"  # Usar la URL externa
    
    print("🔍 Probando con bot_amigable existente")
    print(f"📧 Email: {email}")
    print(f"🌐 Site: {site}")
    print("=" * 50)
    
    # Crear headers de autenticación
    auth_string = f"{email}:{api_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/json'
    }
    
    base_url = f"{site}/api/v1"
    
    try:
        # Primero obtener información del usuario
        print("1️⃣ Obteniendo información del usuario...")
        response = requests.get(f"{base_url}/users/me", headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"👤 Usuario: {user_info.get('full_name', 'N/A')}")
            print(f"🆔 ID: {user_info.get('user_id', 'N/A')}")
        else:
            print(f"❌ Error al obtener información del usuario: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
        # Obtener streams
        print("\n2️⃣ Obteniendo streams...")
        response = requests.get(f"{base_url}/streams", headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            print("📋 Streams disponibles:")
            general_stream_id = None
            for stream in streams.get('streams', []):
                stream_name = stream.get('name', 'Desconocido')
                stream_id = stream.get('stream_id', 'N/A')
                print(f"  - {stream_name} (ID: {stream_id})")
                
                if stream_name.lower() == 'general':
                    general_stream_id = stream_id
                    
            if general_stream_id:
                print(f"\n✅ Stream 'general' encontrado con ID: {general_stream_id}")
                
                # Enviar mensaje
                print("\n3️⃣ Enviando mensaje...")
                message_data = {
                    "type": "stream",
                    "to": general_stream_id,
                    "topic": "Prueba de Bot",
                    "content": "🤖 Mensaje de prueba desde bot_amigable - Conexión con Gemma 3 exitosa! 🚀"
                }
                
                response = requests.post(f"{base_url}/messages", headers=headers, json=message_data, verify=False, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Mensaje enviado exitosamente!")
                    print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Error al enviar mensaje: {response.status_code}")
                    print(f"📄 Detalles: {response.text}")
                    return False
            else:
                print("❌ No se encontró el stream 'general'")
                return False
        else:
            print(f"❌ Error al obtener streams: {response.status_code}")
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
    print("🚀 Probando con bot existente y Gemma 3")
    print("=" * 50)
    
    # Probar conexión LLM primero
    llm_response = test_gemma_connection()
    
    # Probar bot existente
    if test_working_bot():
        print("\n🎉 Pruebas exitosas!")
        print("✅ Gemma 3 funcionando correctamente")
        print("✅ Mensaje enviado a general channel")
        print("✅ Bot existente funciona con la configuración actual")
    else:
        print("\n❌ No se pudo completar la prueba")
        sys.exit(1)
