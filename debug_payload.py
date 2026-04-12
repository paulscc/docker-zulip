#!/usr/bin/env python3
"""
Debug del payload exacto que se envía a Zulip
"""

import requests
import json
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def debug_payload():
    """Debug del payload exacto"""
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    headers = {"Content-Type": "application/json"}
    auth = (bot_email, api_key)
    
    print("=== DEBUG PAYLOAD EXACTO ===")
    
    # Payload exacto que debería funcionar
    payload = {
        "type": "stream",
        "to": "general",
        "topic": "test",
        "content": "Mensaje de prueba debug"
    }
    
    print(f"Payload a enviar:")
    print(json.dumps(payload, indent=2))
    print()
    
    print(f"Headers: {headers}")
    print(f"Auth: {auth}")
    print()
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers,
            json=payload,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        print(f"Response Text: {response.text}")
        
        # Intentar con formato diferente
        print("\n=== INTENTANDO CON FORMATO ALTERNATIVO ===")
        
        payload2 = {
            "type": "stream",
            "to": "general",
            "subject": "test",  # Cambiar topic por subject
            "content": "Mensaje de prueba debug 2"
        }
        
        print(f"Payload alternativo:")
        print(json.dumps(payload2, indent=2))
        
        response2 = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers,
            json=payload2,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response2.status_code}")
        print(f"Response Text: {response2.text}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_payload()
