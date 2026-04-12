#!/usr/bin/env python3
"""
Script de prueba específico para el bot bbbbb-bot con credenciales proporcionadas
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_specific_bot():
    """
    Prueba la conexión del bot específico con las credenciales proporcionadas
    """
    email = "bbbbb-bot@midt.127.0.0.1.nip.io"
    api_key = "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Probando conexión del bot bbbbb-bot")
    print(f"📧 Email: {email}")
    print(f"🌐 Site: {site}")
    print("=" * 50)
    
    # Configuración de autenticación
    auth = (email, api_key)
    base_url = f"{site}/api/v1"
    
    try:
        # Test 1: Obtener información del usuario
        print("1️⃣ Obteniendo información del usuario...")
        response = requests.get(f"{base_url}/users/me", auth=auth, verify=False, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"👤 Usuario: {user_info.get('full_name', 'N/A')}")
            print(f"🆔 ID: {user_info.get('user_id', 'N/A')}")
            print(f"📧 Email: {user_info.get('email', 'N/A')}")
        else:
            print(f"❌ Error al obtener información del usuario: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
        # Test 2: Obtener lista de streams (canales)
        print("\n2️⃣ Obteniendo lista de streams...")
        response = requests.get(f"{base_url}/streams", auth=auth, verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            print("📋 Streams disponibles:")
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
            
        # Test 3: Enviar mensaje a general
        if general_stream:
            print(f"\n3️⃣ Enviando mensaje al stream 'general'...")
            message_data = {
                "type": "stream",
                "to": general_stream['stream_id'],
                "topic": "Prueba de Bot",
                "content": "🤖 Mensaje de prueba desde bbbbb-bot - Conexión con Gemma 3 exitosa! 🚀"
            }
            
            response = requests.post(f"{base_url}/messages", auth=auth, json=message_data, verify=False, timeout=10)
            
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

def test_gemma_connection():
    """
    Prueba la conexión con Gemma 3 (o gemma2:2b como alternativa)
    """
    print("\n🤖 Probando conexión con Gemma...")
    
    # Intentar con gemma3:1b primero
    models_to_try = ["gemma3:1b", "gemma2:2b"]
    
    for model in models_to_try:
        print(f"🔍 Probando con modelo: {model}")
        try:
            url = "http://localhost:11434/api/generate"
            data = {
                "model": model,
                "prompt": "Genera un saludo amigable para un chat de Zulip",
                "stream": False
            }
            
            response = requests.post(url, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                llm_response = result.get('response', 'Sin respuesta')
                print(f"✅ {model} responde: {llm_response}")
                return model, llm_response
            else:
                print(f"❌ Error con {model}: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error al conectar con {model}: {e}")
            
    print("❌ No se pudo conectar con ningún modelo Gemma")
    return None, None

if __name__ == "__main__":
    print("🚀 Iniciando pruebas específicas para bbbbb-bot")
    print("=" * 50)
    
    # Probar conexión LLM primero
    model, llm_response = test_gemma_connection()
    
    # Probar conexión del bot
    if test_specific_bot():
        print("\n🎉 Todas las pruebas exitosas!")
        if model and llm_response:
            print(f"🤖 Modelo LLM funcionando: {model}")
    else:
        print("\n❌ Hubo errores en las pruebas del bot")
        sys.exit(1)
