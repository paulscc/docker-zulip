#!/usr/bin/env python3
"""
Script para probar la conexión de los bots con Zulip y solucionar problemas SSL
"""

import json
import requests
import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from zulip import Client

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_ssl_connection():
    """Prueba diferentes métodos de conexión SSL"""
    
    # Cargar configuración
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    bot_config = config['bots'][0]  # Usar el primer bot para pruebas
    
    print("🔍 Probando conexión SSL con diferentes configuraciones...")
    print("=" * 60)
    
    # Método 1: Sin verificar SSL
    print("\n1. Probando con verify_ssl=False...")
    try:
        client = Client(
            email=bot_config['email'],
            api_key=bot_config['api_key'],
            site=bot_config['server_url'],
            verify_ssl=False
        )
        # Intentar obtener información del servidor
        result = client.get_server_settings()
        print("✅ Conexión exitosa con verify_ssl=False")
        print(f"📋 Servidor: {result.get('realm_name', 'Unknown')}")
    except Exception as e:
        print(f"❌ Error con verify_ssl=False: {e}")
    
    # Método 2: Usar requests directamente
    print("\n2. Probando con requests directas...")
    try:
        url = f"{bot_config['server_url']}/api/v1/server_settings"
        response = requests.get(url, verify=False, timeout=10)
        if response.status_code == 200:
            print("✅ Conexión directa con requests exitosa")
            print(f"📋 Respuesta: {response.json().get('realm_name', 'Unknown')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error con requests: {e}")
    
    # Método 3: Configuración SSL personalizada
    print("\n3. Probando con contexto SSL personalizado...")
    try:
        # Crear un contexto SSL que no verifique certificados
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Usar requests con el contexto SSL
        url = f"{bot_config['server_url']}/api/v1/server_settings"
        response = requests.get(url, verify=ssl_context, timeout=10)
        if response.status_code == 200:
            print("✅ Conexión con contexto SSL personalizado exitosa")
            print(f"📋 Servidor: {response.json().get('realm_name', 'Unknown')}")
        else:
            print(f"❌ Error HTTP: {response.status_code}")
    except Exception as e:
        print(f"❌ Error con contexto SSL: {e}")

def test_bot_message():
    """Prueba enviar un mensaje con diferentes configuraciones"""
    
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    bot_config = config['bots'][0]
    
    print("\n🤖 Probando envío de mensaje...")
    print("=" * 60)
    
    # Intentar con el cliente Zulip modificado
    try:
        # Crear sesión requests personalizada
        session = requests.Session()
        session.verify = False
        
        # Modificar temporalmente el método de requests del cliente
        original_request = requests.request
        requests.request = lambda *args, **kwargs: original_request(*args, **kwargs, verify=False)
        
        client = Client(
            email=bot_config['email'],
            api_key=bot_config['api_key'],
            site=bot_config['server_url']
        )
        
        # Restaurar método original
        requests.request = original_request
        
        # Enviar mensaje
        message_data = {
            "type": "stream",
            "to": "general",
            "topic": "chat",
            "content": "🤖 ¡Hola desde bot_amigable! Test de conexión exitoso. 😊"
        }
        
        result = client.send_message(message_data)
        if result.get('result') == 'success':
            print("✅ Mensaje enviado exitosamente")
            print(f"📝 ID del mensaje: {result.get('id')}")
        else:
            print(f"❌ Error al enviar mensaje: {result.get('msg', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de conexión SSL para bots Zulip")
    print("=" * 60)
    
    test_ssl_connection()
    test_bot_message()
    
    print("\n🎉 Pruebas completadas!")
