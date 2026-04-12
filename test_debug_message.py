#!/usr/bin/env python3
"""
Script para debug del problema de mensaje
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def debug_message_issue():
    """
    Debug del problema con el campo content
    """
    email = "nnnnn-bot@midt.127.0.0.1.nip.io"
    api_key = "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Debug del problema de mensaje")
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
        # Obtener stream ID de general
        response = requests.get(f"{base_url}/streams", headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            general_stream_id = None
            for stream in streams.get('streams', []):
                if stream.get('name', '').lower() == 'general':
                    general_stream_id = stream.get('stream_id')
                    break
                    
            if general_stream_id:
                print(f"✅ Stream 'general' ID: {general_stream_id}")
                
                # Probar con el cliente Zulip para comparar
                print("\n🤖 Intentando con cliente Zulip...")
                try:
                    from zulip import Client
                    
                    # Patch requests para SSL
                    original_request = requests.request
                    requests.request = lambda *args, **kwargs: original_request(*args, **kwargs, verify=False)
                    
                    try:
                        client = Client(
                            email=email,
                            api_key=api_key,
                            site=site
                        )
                        
                        message_data = {
                            "type": "stream",
                            "to": general_stream_id,
                            "topic": "Prueba de Bot",
                            "content": "🤖 Mensaje de prueba desde nnnnn-bot via cliente Zulip! 🚀"
                        }
                        
                        result = client.send_message(message_data)
                        print(f"✅ Cliente Zulip funcionó!")
                        print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                        print(f"📄 Resultado: {result}")
                        return True
                        
                    finally:
                        requests.request = original_request
                        
                except Exception as e:
                    print(f"❌ Error con cliente Zulip: {e}")
                
                # Si el cliente no funciona, probar con formato raw
                print("\n📤 Probando con formato raw...")
                raw_data = json.dumps({
                    "type": "stream",
                    "to": general_stream_id,
                    "topic": "Prueba de Bot",
                    "content": "🤖 Mensaje de prueba desde nnnnn-bot - Raw JSON! 🚀"
                })
                
                raw_headers = headers.copy()
                raw_headers['Content-Length'] = str(len(raw_data))
                
                response = requests.post(f"{base_url}/messages", data=raw_data, headers=raw_headers, verify=False, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Raw JSON funcionó!")
                    print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Raw JSON falló: {response.status_code}")
                    print(f"📄 Detalles: {response.text}")
                    
                    # Mostrar el request enviado
                    print(f"\n📋 Request enviado:")
                    print(f"URL: {base_url}/messages")
                    print(f"Headers: {raw_headers}")
                    print(f"Data: {raw_data}")
                
                return False
            else:
                print("❌ No se encontró el stream 'general'")
                return False
        else:
            print(f"❌ Error al obtener streams: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Debug del problema de mensaje")
    print("=" * 50)
    
    if debug_message_issue():
        print("\n🎉 Problema resuelto!")
    else:
        print("\n❌ Problema persiste")
        sys.exit(1)
