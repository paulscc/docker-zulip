#!/usr/bin/env python3
"""
Script para probar y arreglar el envío de mensaje
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_message_fix():
    """
    Probar diferentes formatos de mensaje
    """
    email = "nnnnn-bot@midt.127.0.0.1.nip.io"
    api_key = "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Probando formato de mensaje corregido")
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
        # Obtener streams para encontrar el ID de general
        response = requests.get(f"{base_url}/streams", headers=headers, verify=False, timeout=10)
        
        if response.status_code == 200:
            streams = response.json()
            general_stream_id = None
            for stream in streams.get('streams', []):
                if stream.get('name', '').lower() == 'general':
                    general_stream_id = stream.get('stream_id')
                    break
                    
            if general_stream_id:
                print(f"✅ Stream 'general' encontrado con ID: {general_stream_id}")
                
                # Probar diferentes formatos de mensaje
                message_formats = [
                    {
                        "name": "Formato estándar",
                        "data": {
                            "type": "stream",
                            "to": general_stream_id,
                            "topic": "Prueba de Bot",
                            "content": "🤖 Mensaje de prueba desde nnnnn-bot - Conexión con Gemma 3 exitosa! 🚀"
                        }
                    },
                    {
                        "name": "Formato con strings",
                        "data": {
                            "type": "stream",
                            "to": str(general_stream_id),
                            "topic": "Prueba de Bot",
                            "content": "🤖 Mensaje de prueba desde nnnnn-bot - Formato strings! 🚀"
                        }
                    },
                    {
                        "name": "Formato simple",
                        "data": {
                            "type": "stream",
                            "to": general_stream_id,
                            "subject": "Prueba de Bot",
                            "content": "🤖 Mensaje de prueba desde nnnnn-bot - Formato simple! 🚀"
                        }
                    }
                ]
                
                for msg_format in message_formats:
                    print(f"\n📤 Probando {msg_format['name']}...")
                    response = requests.post(f"{base_url}/messages", headers=headers, json=msg_format['data'], verify=False, timeout=10)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"✅ {msg_format['name']} funcionó!")
                        print(f"🆔 ID del mensaje: {result.get('id', 'N/A')}")
                        return True
                    else:
                        print(f"❌ {msg_format['name']} falló: {response.status_code}")
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
    print("🚀 Probando formatos de mensaje")
    print("=" * 50)
    
    if test_message_fix():
        print("\n🎉 Mensaje enviado exitosamente!")
    else:
        print("\n❌ No se pudo enviar el mensaje")
        sys.exit(1)
