#!/usr/bin/env python3
"""
Probar conexión HTTP con Zulip
"""

import requests
import base64
import json

def test_http_connection():
    """Probar si Zulip responde por HTTP"""
    
    # Configuración del bot
    email = "ccccc-bot@midt.127.0.0.1.nip.io"
    api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
    
    # URLs a probar
    urls = [
        "http://midt.127.0.0.1.nip.io",
        "http://localhost:9991",
        "http://127.0.0.1:9991"
    ]
    
    print("🌐 Probando conexiones HTTP...")
    print("=" * 50)
    
    for url in urls:
        print(f"\n🔍 Probando: {url}")
        
        try:
            # 1. Probar server settings
            server_url = f"{url}/api/v1/server_settings"
            response = requests.get(server_url, timeout=10)
            
            print(f"   Server Settings Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Servidor accesible!")
                print(f"   🏢 Realm: {data.get('realm_name', 'Unknown')}")
                
                # 2. Probar autenticación
                auth_string = f"{email}:{api_key}"
                auth_header = base64.b64encode(auth_string.encode()).decode()
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Basic {auth_header}"
                }
                
                auth_url = f"{url}/api/v1/users/me"
                auth_response = requests.get(auth_url, headers=headers, timeout=10)
                
                print(f"   Auth Status: {auth_response.status_code}")
                
                if auth_response.status_code == 200:
                    user_data = auth_response.json()
                    print(f"   ✅ Bot autenticado: {user_data.get('full_name', 'Unknown')}")
                    
                    # 3. Probar enviar mensaje
                    message_data = {
                        "type": "stream",
                        "to": "general",
                        "subject": "chat",
                        "content": "¡Hola desde HTTP! Bot funcionando correctamente."
                    }
                    
                    msg_url = f"{url}/api/v1/messages"
                    msg_response = requests.post(msg_url, json=message_data, headers=headers, timeout=10)
                    
                    print(f"   Message Status: {msg_response.status_code}")
                    print(f"   Response: {msg_response.text}")
                    
                    if msg_response.status_code == 200:
                        result = msg_response.json()
                        if result.get('result') == 'success':
                            print(f"   ✅ MENSAJE ENVIADO! ID: {result.get('id')}")
                            return url  # Devolver la URL que funcionó
                    
                else:
                    print(f"   ❌ Error autenticación: {auth_response.text}")
            else:
                print(f"   ❌ Error servidor: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
    
    return None

def update_config_for_http(http_url):
    """Actualizar configuración para usar HTTP"""
    print(f"\n🔧 Actualizando configuración para HTTP: {http_url}")
    
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Actualizar todos los bots para usar HTTP
        for bot in config['bots']:
            bot['server_url'] = http_url
        
        with open('bot_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuración actualizada para HTTP")
        return True
        
    except Exception as e:
        print(f"❌ Error actualizando configuración: {e}")
        return False

if __name__ == "__main__":
    working_url = test_http_connection()
    
    if working_url:
        print(f"\n🎉 Se encontró URL funcional: {working_url}")
        if update_config_for_http(working_url):
            print("🚀 Los bots están listos para usar HTTP!")
        else:
            print("❌ Error actualizando la configuración")
    else:
        print("\n❌ No se encontró ninguna URL HTTP funcional")
