#!/usr/bin/env python3
"""
Probar con form-data en lugar de JSON
"""

import requests
import json
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def test_form_data():
    """Probar con form-data"""
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    auth = (bot_email, api_key)
    
    print("=== PROBANDO CON FORM-DATA ===")
    
    # Intentar con form-data
    try:
        data = {
            "type": "stream",
            "to": "general",
            "topic": "test",
            "content": "Mensaje de prueba con form-data"
        }
        
        response = requests.post(
            f"{server_url}/api/v1/messages",
            data=data,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("¡ÉXITO con form-data!")
            return True
        else:
            print("Error con form-data")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_simple_json():
    """Probar JSON simple sin headers personalizados"""
    
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    auth = (bot_email, api_key)
    
    print("\n=== PROBANDO JSON SIMPLE ===")
    
    try:
        payload = {
            "type": "stream",
            "to": "general",
            "topic": "test",
            "content": "Mensaje de prueba JSON simple"
        }
        
        # Sin Content-Type header, dejar que requests lo agregue
        response = requests.post(
            f"{server_url}/api/v1/messages",
            json=payload,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("¡ÉXITO con JSON simple!")
            return True
        else:
            print("Error con JSON simple")
            return False
            
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("=== PROBANDO DIFERENTES FORMATOS ===")
    
    form_data_ok = test_form_data()
    json_simple_ok = test_simple_json()
    
    print(f"\n=== RESULTADOS ===")
    print(f"Form-data: {'OK' if form_data_ok else 'ERROR'}")
    print(f"JSON simple: {'OK' if json_simple_ok else 'ERROR'}")
    
    if form_data_ok or json_simple_ok:
        print("\n¡Tenemos un formato que funciona!")
    else:
        print("\nNingún formato funciona")

if __name__ == "__main__":
    main()
