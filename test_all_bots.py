#!/usr/bin/env python3
"""
Script para probar las conexiones de todos los bots
"""

import requests
import json
import sys
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64
import time

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def test_bot_connection(bot_config):
    """
    Probar conexión de un bot individual
    """
    email = bot_config['email']
    api_key = bot_config['api_key']
    site = bot_config['server_url']
    bot_name = bot_config['bot_name']
    
    # Crear headers de autenticación
    auth_string = f"{email}:{api_key}"
    auth_bytes = auth_string.encode('ascii')
    auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
    
    headers = {
        'Authorization': f'Basic {auth_b64}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    base_url = f"{site}/api/v1"
    
    try:
        # Test 1: Obtener información del usuario
        response = requests.get(f"{base_url}/users/me", headers={'Authorization': f'Basic {auth_b64}'}, verify=False, timeout=10)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"  - {bot_name}: {user_info.get('full_name', 'N/A')} (ID: {user_info.get('user_id', 'N/A')})")
            return True
        else:
            print(f"  - {bot_name}: Error {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  - {bot_name}: Error de conexión")
        return False

def test_all_bots():
    """
    Probar todos los bots configurados
    """
    print("Probando conexiones de todos los bots...")
    print("=" * 50)
    
    try:
        # Leer configuración
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Obtener solo los 8 bots nuevos
        new_bot_names = ['nnnnn-bot', 'aaaaa-bot', 'tt-bot', 'yy-bot', 'uu-bot', 'ii-bot', 'yyyyy-bot', 'ffff-bot']
        new_bots = [bot for bot in config['bots'] if bot['bot_name'] in new_bot_names]
        
        print(f"Encontrados {len(new_bots)} bots nuevos:")
        
        successful_connections = 0
        for bot in new_bots:
            if test_bot_connection(bot):
                successful_connections += 1
            time.sleep(0.5)  # Pequeña pausa entre pruebas
        
        print(f"\nResumen: {successful_connections}/{len(new_bots)} bots conectados exitosamente")
        
        if successful_connections == len(new_bots):
            print("¡Todos los bots están listos para iniciar!")
            return True
        else:
            print("Algunos bots tienen problemas de conexión")
            return False
            
    except Exception as e:
        print(f"Error al probar bots: {e}")
        return False

if __name__ == "__main__":
    print("Probando todos los bots...")
    print("=" * 50)
    
    if test_all_bots():
        print("\nPruebas completadas exitosamente")
    else:
        print("\nHubo errores en las pruebas")
        sys.exit(1)
