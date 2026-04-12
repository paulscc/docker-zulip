#!/usr/bin/env python3
"""
Script para diagnosticar problemas de conexión con la API de Zulip
"""

import json
import requests
import base64
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_api_key_directly():
    """Prueba la API key directamente con curl/requests"""
    
    # Cargar configuración
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    bot_config = config['bots'][1]  # bot_tecnico
    
    print("🔍 Diagnosticando conexión con API de Zulip")
    print("=" * 60)
    print(f"🤖 Bot: {bot_config['bot_name']}")
    print(f"📧 Email: {bot_config['email']}")
    print(f"🔑 API Key: {bot_config['api_key'][:20]}...")
    print(f"🌐 Servidor: {bot_config['server_url']}")
    
    # Método 1: Autenticación Basic
    print("\n1. Probando autenticación Basic...")
    try:
        url = f"{bot_config['server_url']}/api/v1/users/me"
        auth_string = f"{bot_config['email']}:{bot_config['api_key']}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Conexión exitosa!")
            print(f"   👤 Usuario: {data.get('full_name', 'Unknown')}")
            print(f"   📧 Email: {data.get('email', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Método 2: API key en header
    print("\n2. Probando con API key en header...")
    try:
        url = f"{bot_config['server_url']}/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {bot_config['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Conexión exitosa!")
            print(f"   👤 Usuario: {data.get('full_name', 'Unknown')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    # Método 3: Formulario de login
    print("\n3. Probando con formulario de login...")
    try:
        url = f"{bot_config['server_url']}/api/v1/fetch_api_key"
        data = {
            "username": bot_config['email'].replace('-bot@localhost', ''),
            "password": bot_config['api_key']
        }
        
        response = requests.post(url, json=data, verify=False, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"   ✅ Login exitoso!")
            print(f"   🔑 Nueva API Key: {result.get('api_key', 'Unknown')[:20]}...")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
    
    return False

def test_server_info():
    """Prueba obtener información del servidor"""
    print("\n🌐 Probando información del servidor...")
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        bot_config = config['bots'][0]
        url = f"{bot_config['server_url']}/api/v1/server_settings"
        
        response = requests.get(url, verify=False, timeout=10)
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Servidor accesible!")
            print(f"   🏢 Realm: {data.get('realm_name', 'Unknown')}")
            print(f"   🌐 URL: {data.get('realm_uri', 'Unknown')}")
            print(f"   📧 Email: {data.get('realm_email_auth_enabled', 'Unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Excepción: {e}")

if __name__ == "__main__":
    test_server_info()
    success = test_api_key_directly()
    
    if success:
        print("\n🎉 La API key funciona correctamente!")
        print("📝 El problema puede estar en el framework de los bots.")
    else:
        print("\n❌ La API key no es válida o hay un problema de autenticación.")
        print("🔧 Verifica:")
        print("   1. Que el bot esté creado correctamente en Zulip")
        print("   2. Que estés usando la API key correcta")
        print("   3. Que el email del bot sea correcto")
