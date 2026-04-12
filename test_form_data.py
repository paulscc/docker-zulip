#!/usr/bin/env python3
"""
Script para probar con form data en lugar de JSON
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_form_data():
    """
    Probar envío usando form data
    """
    email = "nnnnn-bot@midt.127.0.0.1.nip.io"
    api_key = "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Probando con form data")
    print("=" * 50)
    
    # Crear headers de autenticación
    auth_string = f"{email}:{api_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    base_url = f"{site}/api/v1"
    
    try:
        # Obtener stream ID de general
        response = requests.get(f"{base_url}/streams", headers={'Authorization': f'Basic {auth_b64}'}, verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            general_stream_id = None
            for stream in streams.get('streams', []):
                if stream.get('name', '').lower() == 'general':
                    general_stream_id = stream.get('stream_id')
                    break
                    
            if general_stream_id:
                print(f"✅ Stream 'general' ID: {general_stream_id}")
                
                # Probar con form data
                print("\n📤 Probando con form data...")
                form_data = {
                    'type': 'stream',
                    'to': str(general_stream_id),
                    'topic': 'Prueba de Bot',
                    'content': '🤖 Mensaje de prueba desde nnnnn-bot via form data! 🚀'
                }
                
                headers = {
                    'Authorization': f'Basic {auth_b64}',
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
                
                response = requests.post(f"{base_url}/messages", data=form_data, headers=headers, verify=False, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Form data funcionó!")
                    print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Form data falló: {response.status_code}")
                    print(f"📄 Detalles: {response.text}")
                
                # Probar con multipart form data
                print("\n📤 Probando con multipart form data...")
                files = {}
                data = {
                    'type': (None, 'stream'),
                    'to': (None, str(general_stream_id)),
                    'topic': (None, 'Prueba de Bot'),
                    'content': (None, '🤖 Mensaje de prueba desde nnnnn-bot via multipart! 🚀')
                }
                
                headers = {
                    'Authorization': f'Basic {auth_b64}'
                }
                
                response = requests.post(f"{base_url}/messages", files=files, data=data, headers=headers, verify=False, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Multipart funcionó!")
                    print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                    return True
                else:
                    print(f"❌ Multipart falló: {response.status_code}")
                    print(f"📄 Detalles: {response.text}")
                
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
    print("🚀 Probando form data")
    print("=" * 50)
    
    if test_form_data():
        print("\n🎉 Mensaje enviado exitosamente!")
    else:
        print("\n❌ No se pudo enviar el mensaje")
        sys.exit(1)
