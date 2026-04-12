#!/usr/bin/env python3
"""
Verificar streams disponibles en Zulip
"""

import requests
import json
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def check_streams():
    """Verificar streams disponibles"""
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    headers = {"Content-Type": "application/json"}
    auth = (bot_email, api_key)
    
    print("=== VERIFICANDO STREAMS DISPONIBLES ===")
    
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
            
            for stream in streams:
                print(f"  - {stream['name']} (ID: {stream['stream_id']})")
            
            return streams
        else:
            print(f"Error: {response.status_code}")
            print(f"Response: {response.text}")
            return []
            
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    streams = check_streams()
