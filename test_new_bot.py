#!/usr/bin/env python3
"""
Script para probar el nuevo bot nnnnn-bot
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_new_bot():
    """
    Probar conexión del nuevo bot nnnnn-bot
    """
    email = "nnnnn-bot@midt.127.0.0.1.nip.io"
    api_key = "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Probando nuevo bot nnnnn-bot")
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
        # Test 1: Obtener información del usuario
        print("1️⃣ Obteniendo información del usuario...")
        response = requests.get(f"{base_url}/users/me", headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"👤 Usuario: {user_info.get('full_name', 'N/A')}")
            print(f"🆔 ID: {user_info.get('user_id', 'N/A')}")
            print(f"📧 Email: {user_info.get('email', 'N/A')}")
            print(f"🤖 Tipo de bot: {user_info.get('is_bot', 'N/A')}")
        else:
            print(f"❌ Error al obtener información del usuario: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
        # Test 2: Obtener lista de streams
        print("\n2️⃣ Obteniendo lista de streams...")
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
                    
        else:
            print(f"❌ Error al obtener streams: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
        # Test 3: Enviar mensaje a general
        if general_stream_id:
            print(f"\n3️⃣ Enviando mensaje al stream 'general'...")
            message_data = {
                "type": "stream",
                "to": general_stream_id,
                "topic": "Prueba de Bot",
                "content": "🤖 Mensaje de prueba desde nnnnn-bot - Conexión con Gemma 3 exitosa! 🚀"
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
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False

def test_gemma_integration():
    """
    Prueba la integración con Gemma 3
    """
    print("\n🤖 Probando integración con Gemma...")
    
    try:
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "gemma3:1b",
            "prompt": "Genera un mensaje amigable para un chat de Zulip desde el bot nnnnn-bot",
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

def update_bot_config():
    """
    Actualizar la configuración del bot en bot_config.json
    """
    print("\n📝 Actualizando configuración del bot...")
    
    try:
        # Leer configuración existente
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Buscar si ya existe el bot
        existing_bot = None
        for i, bot in enumerate(config['bots']):
            if bot['email'] == "nnnnn-bot@midt.127.0.0.1.nip.io":
                existing_bot = i
                break
        
        new_bot_config = {
            "bot_name": "nnnnn-bot",
            "email": "nnnnn-bot@midt.127.0.0.1.nip.io",
            "api_key": "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": [
                {"stream": "general", "topic": "chat"}
            ],
            "message_interval": 30,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False
        }
        
        if existing_bot is not None:
            # Actualizar bot existente
            config['bots'][existing_bot] = new_bot_config
            print(f"✅ Bot existente actualizado")
        else:
            # Añadir nuevo bot
            config['bots'].append(new_bot_config)
            print(f"✅ Nuevo bot añadido")
        
        # Guardar configuración
        with open('bot_config.json', 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuración guardada en bot_config.json")
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar configuración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Probando nuevo bot nnnnn-bot")
    print("=" * 50)
    
    # Actualizar configuración del bot
    update_bot_config()
    
    # Probar conexión LLM primero
    llm_response = test_gemma_integration()
    
    # Probar conexión del bot
    if test_new_bot():
        print("\n🎉 Todas las pruebas exitosas!")
        print("✅ nnnnn-bot conectado correctamente")
        print("✅ Mensaje enviado a general channel")
        if llm_response:
            print("✅ Gemma 3 funcionando correctamente")
    else:
        print("\n❌ Hubo errores en las pruebas")
        sys.exit(1)
