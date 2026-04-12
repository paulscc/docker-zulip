#!/usr/bin/env python3
"""
Test final con enfoque diferente para enviar mensajes
"""

import ssl
import urllib3
import requests
import base64
import json
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

# Configurar SSL global
ssl._create_default_https_context = ssl._create_unverified_context

def send_message_working():
    """Intento final con configuración SSL global"""
    
    # Configuración del bot
    email = "ccccc-bot@midt.127.0.0.1.nip.io"
    api_key = "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN"
    server_url = "https://midt.127.0.0.1.nip.io"
    
    print("🚀 Intento final con SSL global...")
    print("=" * 50)
    
    try:
        # Crear sesión con SSL deshabilitado
        session = requests.Session()
        session.verify = False
        session.mount('https://', requests.adapters.HTTPAdapter(max_retries=3))
        
        # Autenticación
        auth_string = f"{email}:{api_key}"
        auth_header = base64.b64encode(auth_string.encode()).decode()
        
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {auth_header}",
            "User-Agent": "ZulipBot/1.0"
        }
        
        # 1. Verificar autenticación
        print("🔐 Verificando autenticación...")
        auth_url = f"{server_url}/api/v1/users/me"
        auth_response = session.get(auth_url, headers=headers, timeout=10)
        
        if auth_response.status_code != 200:
            print(f"❌ Error de autenticación: {auth_response.text}")
            return False
        
        user_data = auth_response.json()
        print(f"✅ Autenticado como: {user_data.get('full_name', 'Unknown')}")
        
        # 2. Enviar mensaje con formato estricto
        print("📝 Enviando mensaje...")
        
        # Probar diferentes payloads
        payloads = [
            {
                "name": "Formato estándar",
                "data": {
                    "type": "stream",
                    "to": "general",
                    "subject": "chat",
                    "content": "Hola desde bot_amigable - prueba final!"
                }
            },
            {
                "name": "Formato alternativo",
                "data": {
                    "type": "stream",
                    "to": "general",
                    "topic": "chat",
                    "content": "Hola desde bot_amigable - prueba final!"
                }
            }
        ]
        
        for payload in payloads:
            print(f"\n🧪 Probando: {payload['name']}")
            print(f"   Data: {json.dumps(payload['data'], ensure_ascii=False)}")
            
            msg_url = f"{server_url}/api/v1/messages"
            msg_response = session.post(
                msg_url, 
                json=payload['data'], 
                headers=headers, 
                timeout=15
            )
            
            print(f"   Status: {msg_response.status_code}")
            print(f"   Response: {msg_response.text}")
            
            if msg_response.status_code == 200:
                result = msg_response.json()
                if result.get('result') == 'success':
                    print(f"   ✅ ÉXITO! Message ID: {result.get('id')}")
                    return True
            
        return False
        
    except Exception as e:
        print(f"❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_message_working()
    if success:
        print("\n🎉 Los bots están listos para funcionar!")
        print("📝 Ahora podemos activar los bots con el framework actualizado.")
    else:
        print("\n❌ No se pudo resolver el problema de envío de mensajes.")
