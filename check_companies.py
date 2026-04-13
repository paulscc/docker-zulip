#!/usr/bin/env python3
"""
Script para verificar qué compañías (realms) están creadas en Zulip
"""

import json
import requests
import base64
from urllib3.exceptions import InsecureRequestWarning
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

def get_server_info(server_url, bot_email, bot_api_key):
    """Obtiene información del servidor Zulip"""
    try:
        # Intentar obtener server settings (no requiere autenticación)
        url = f"{server_url}/api/v1/server_settings"
        response = requests.get(url, verify=False, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'success': True,
                'realm_name': data.get('realm_name', 'Unknown'),
                'realm_uri': data.get('realm_uri', 'Unknown'),
                'realm_description': data.get('realm_description', 'No description'),
                'authentication_methods': data.get('authentication_methods', {}),
                'email_auth_enabled': data.get('email_auth_enabled', False)
            }
        else:
            return {'success': False, 'error': f"HTTP {response.status_code}: {response.text}"}
            
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    # Cargar configuración de bots
    with open('bot_config.json', 'r') as f:
        config = json.load(f)
    
    # Extraer URLs únicas de servidores
    servers = {}
    for bot in config['bots']:
        server_url = bot['server_url']
        if server_url not in servers:
            servers[server_url] = {
                'bots': [],
                'info': None
            }
        servers[server_url]['bots'].append(bot['bot_name'])
    
    print("=== COMPANÍAS (REALMS) ENCONTRADAS EN ZULIP ===")
    print("=" * 60)
    
    for server_url, server_data in servers.items():
        print(f"\n\nServidor: {server_url}")
        print("-" * 40)
        print(f"Bots configurados: {', '.join(server_data['bots'])}")
        
        # Intentar obtener información del servidor
        # Usar el primer bot de este servidor para autenticación
        bot = next((b for b in config['bots'] if b['server_url'] == server_url), None)
        if bot:
            print(f"Probando con bot: {bot['bot_name']}")
            info = get_server_info(server_url, bot['email'], bot['api_key'])
            
            if info['success']:
                print(f"  Realm Name: {info['realm_name']}")
                print(f"  Realm URI: {info['realm_uri']}")
                print(f"  Descripción: {info['realm_description']}")
                print(f"  Email Auth: {info['email_auth_enabled']}")
            else:
                print(f"  Error: {info['error']}")
        else:
            print("  No se encontró bot para probar conexión")

if __name__ == "__main__":
    main()
