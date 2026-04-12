#!/usr/bin/env python3
"""
Test simple para fff-bot con Gemma2
Verifica conexión y envía mensajes de prueba
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_connection():
    """Probar conexión básica"""
    print("=== PROBANDO CONEXIÓN ===")
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    headers = {"Content-Type": "application/json"}
    auth = (bot_email, api_key)
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"Conexión exitosa: {user_data.get('full_name', 'Unknown')}")
            print(f"User ID: {user_data.get('user_id', 'Unknown')}")
            return True, auth, headers, server_url
        else:
            print(f"Error de conexión: {response.status_code}")
            print(f"Response: {response.text}")
            return False, None, None, None
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False, None, None, None

def get_available_streams(auth, headers, server_url):
    """Obtener lista de streams disponibles"""
    print("\n=== OBTENIENDO STREAMS DISPONIBLES ===")
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/streams",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            streams = response.json().get('streams', [])
            print(f"Streams encontrados: {len(streams)}")
            
            for stream in streams[:10]:  # Mostrar primeros 10
                print(f"  - {stream.get('name', 'Unknown')} (ID: {stream.get('stream_id', 'Unknown')})")
            
            return streams
        else:
            print(f"Error al obtener streams: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error al obtener streams: {e}")
        return []

def test_gemma2():
    """Probar conexión con Gemma2"""
    print("\n=== PROBANDO GEMMA2 ===")
    
    try:
        payload = {
            "model": "gemma2",
            "prompt": "Hola, ¿cómo estás?",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            response_text = result.get("response", "")
            print(f"Gemma2 funciona: {response_text[:100]}...")
            return True
        else:
            print(f"Error con Gemma2: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error con Gemma2: {e}")
        return False

def send_test_message(auth, headers, server_url, stream_name):
    """Enviar mensaje de prueba a un stream específico"""
    print(f"\n=== ENVIANDO MENSAJE A #{stream_name} ===")
    
    payload = {
        "type": "stream",
        "to": stream_name,
        "topic": "prueba",
        "content": f"Mensaje de prueba desde fff-bot con Gemma2\n\n*Enviado: {datetime.now().strftime('%H:%M:%S')}*"
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers,
            json=payload,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Mensaje enviado exitosamente a #{stream_name}")
            return True
        else:
            print(f"Error al enviar mensaje: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error al enviar mensaje: {e}")
        return False

def send_gemma2_message(auth, headers, server_url, stream_name):
    """Enviar mensaje generado por Gemma2"""
    print(f"\n=== ENVIANDO MENSAJE GEMMA2 A #{stream_name} ===")
    
    # Generar mensaje con Gemma2
    try:
        payload = {
            "model": "gemma2",
            "prompt": "Genera un mensaje corto, positivo y amigable para un chat de equipo (máximo 2 líneas)",
            "stream": False
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"Error generando mensaje con Gemma2: {response.status_code}")
            return False
        
        gemma_response = response.json()
        message_content = gemma_response.get("response", "")
        
        # Enviar mensaje a Zulip
        zulip_payload = {
            "type": "stream",
            "to": stream_name,
            "topic": "gemma2",
            "content": f"{message_content}\n\n*Generado por Gemma2 - {datetime.now().strftime('%H:%M:%S')}*"
        }
        
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers,
            json=zulip_payload,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"Mensaje de Gemma2 enviado exitosamente a #{stream_name}")
            print(f"Contenido: {message_content}")
            return True
        else:
            print(f"Error al enviar mensaje de Gemma2: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Función principal"""
    print("=== TEST FFF-BOT CON GEMMA2 ===")
    
    # 1. Probar conexión
    connected, auth, headers, server_url = test_connection()
    if not connected:
        print("\nNo se puede conectar. Revisa:")
        print("1. Que el servidor Zulip esté funcionando")
        print("2. Las credenciales del bot")
        print("3. La URL del servidor")
        return
    
    # 2. Probar Gemma2
    gemma2_works = test_gemma2()
    if not gemma2_works:
        print("\nGemma2 no responde. Revisa:")
        print("1. Que Ollama esté funcionando")
        print("2. Que el modelo gemma2 esté instalado")
        print("3. Ejecuta: ollama pull gemma2")
        return
    
    # 3. Obtener streams disponibles
    streams = get_available_streams(auth, headers, server_url)
    
    if not streams:
        print("\nNo hay streams disponibles. Intentando crear uno...")
        # Intentar con stream por defecto
        stream_name = "general"
        print("Usando stream 'general' por defecto")
    else:
        # Usar el primer stream disponible
        stream_name = streams[0].get('name', 'general')
        print(f"Usando stream: {stream_name}")
    
    # 4. Enviar mensaje de prueba
    if send_test_message(auth, headers, server_url, stream_name):
        print("\nMensaje de prueba enviado correctamente")
        
        # 5. Enviar mensaje con Gemma2
        if send_gemma2_message(auth, headers, server_url, stream_name):
            print("\n¡ÉXITO! fff-bot con Gemma2 funciona correctamente")
            print("\nAhora puedes usar:")
            print("python fff_bot_gemma2.py")
        else:
            print("\nError al enviar mensaje con Gemma2")
    else:
        print("\nError al enviar mensaje de prueba")

if __name__ == "__main__":
    main()
