#!/usr/bin/env python3
"""
Debug para Gemma2 y Zulip
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_gemma2_simple():
    """Probar Gemma2 con un request simple"""
    print("=== PROBANDO GEMMA2 ===")
    
    try:
        payload = {
            "model": "gemma2:2b",
            "prompt": "Hola",
            "stream": False
        }
        
        print(f"Enviando a Ollama: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response JSON: {json.dumps(result, indent=2)}")
            return True
        else:
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_zulip_simple():
    """Probar Zulip con un mensaje simple"""
    print("\n=== PROBANDO ZULIP ===")
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    headers = {"Content-Type": "application/json"}
    auth = (bot_email, api_key)
    
    # Probar conexión primero
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Conexión Status: {response.status_code}")
        if response.status_code == 200:
            print("Conexión OK")
        else:
            print(f"Error conexión: {response.text}")
            return False
    except Exception as e:
        print(f"Error conexión: {e}")
        return False
    
    # Probar enviar mensaje simple
    try:
        payload = {
            "type": "stream",
            "to": "general",
            "topic": "test",
            "content": "Mensaje de prueba simple"
        }
        
        print(f"Enviando a Zulip: {json.dumps(payload, indent=2)}")
        
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers,
            json=payload,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Error enviando mensaje: {e}")
        return False

def main():
    print("=== DEBUG GEMMA2 + ZULIP ===")
    
    # Probar Gemma2
    gemma2_ok = test_gemma2_simple()
    
    # Probar Zulip
    zulip_ok = test_zulip_simple()
    
    print(f"\n=== RESULTADOS ===")
    print(f"Gemma2: {'OK' if gemma2_ok else 'ERROR'}")
    print(f"Zulip: {'OK' if zulip_ok else 'ERROR'}")
    
    if gemma2_ok and zulip_ok:
        print("\n¡Todo funciona! El problema debe estar en el flujo combinado.")
    else:
        print("\nHay problemas básicos que resolver primero.")

if __name__ == "__main__":
    main()
