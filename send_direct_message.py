#!/usr/bin/env python3
"""
Script para enviar mensaje directo a Zulip usando requests
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def send_message_direct():
    """
    Enviar mensaje directo usando API requests
    """
    email = "bbbbb-bot@midt.127.0.0.1.nip.io"
    api_key = "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv"
    site = "https://midt.127.0.0.1.nip.io"
    
    print("🔍 Enviando mensaje directo con requests")
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
        # Primero obtener streams para encontrar el ID de "general"
        print("1️⃣ Obteniendo streams...")
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
                    
            if general_stream_id:
                print(f"\n✅ Stream 'general' encontrado con ID: {general_stream_id}")
                
                # Enviar mensaje
                print("\n2️⃣ Enviando mensaje...")
                message_data = {
                    "type": "stream",
                    "to": general_stream_id,
                    "topic": "Prueba de Bot",
                    "content": "🤖 Mensaje de prueba desde bbbbb-bot - Conexión con Gemma 3 exitosa! 🚀"
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
        else:
            print(f"❌ Error al obtener streams: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Enviando mensaje directo a Zulip")
    print("=" * 50)
    
    if send_message_direct():
        print("\n🎉 Mensaje enviado exitosamente!")
    else:
        print("\n❌ No se pudo enviar el mensaje")
        sys.exit(1)
