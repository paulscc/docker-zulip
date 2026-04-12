#!/usr/bin/env python3
"""
Prueba con SSL bypass para certificado autofirmado
"""

import ssl
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import requests
import base64
import json

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_with_ssl_bypass():
    """Prueba con SSL deshabilitado"""
    
    # Configuración del bot
    email = "ccccc-bot@midt.127.0.0.1.nip.io"
    api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
    server_url = "https://midt.127.0.0.1.nip.io"
    
    # Crear sesión personalizada con SSL deshabilitado
    session = requests.Session()
    session.verify = False
    
    # Headers de autenticación
    auth_string = f"{email}:{api_key}"
    auth_header = base64.b64encode(auth_string.encode()).decode()
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Basic {auth_header}"
    }
    
    print("🔓 Probando con SSL bypass...")
    print("=" * 50)
    
    # 1. Probar conexión básica
    try:
        url = f"{server_url}/api/v1/users/me"
        response = session.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"👤 Bot: {data.get('full_name', 'Unknown')}")
            
            # 2. Enviar mensaje
            message_data = {
                "type": "stream",
                "to": "general",
                "subject": "chat",
                "content": "Hola desde bot_amigable con SSL bypass!"
            }
            
            print(f"\n📝 Enviando mensaje...")
            url = f"{server_url}/api/v1/messages"
            response = session.post(url, json=message_data, headers=headers, timeout=10)
            
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Mensaje enviado! ID: {result.get('id')}")
                return True
            else:
                print(f"❌ Error al enviar mensaje")
                return False
                
        else:
            print(f"❌ Error de autenticación: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Excepción: {e}")
        return False

if __name__ == "__main__":
    test_with_ssl_bypass()
