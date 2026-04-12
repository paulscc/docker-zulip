#!/usr/bin/env python3
"""
Diagnóstico Completo de API Keys
Investigar todas las posibles causas del error Malformed API key
"""

import requests
import json
import base64
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probar_metodo_bearer(api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar autenticación con Bearer token"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"Bearer token: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"Bearer token: ERROR - {e}")
        return False

def probar_metodo_basic(api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar autenticación con HTTP Basic"""
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"HTTP Basic: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"HTTP Basic: ERROR - {e}")
        return False

def probar_metodo_basic_con_usuario(email, api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar autenticación con email como usuario y API key como password"""
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (email, api_key)
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        print(f"HTTP Basic (email:key): {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"HTTP Basic (email:key): ERROR - {e}")
        return False

def probar_metodo_header_custom(api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar con header personalizado"""
    
    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            verify=False,
            timeout=10
        )
        
        print(f"X-API-Key header: {response.status_code}")
        if response.status_code != 200:
            print(f"  Response: {response.text}")
        return response.status_code == 200
        
    except Exception as e:
        print(f"X-API-Key header: ERROR - {e}")
        return False

def probar_diferentes_endpoints(api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar diferentes endpoints para ver si funciona en alguno"""
    
    endpoints = [
        "/api/v1/users/me",
        "/api/v1/server_settings",
        "/api/v1/streams",
        "/api/v1/realm"
    ]
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")
    
    for endpoint in endpoints:
        try:
            response = requests.get(
                f"{server_url}{endpoint}",
                headers=headers,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            print(f"Endpoint {endpoint}: {response.status_code}")
            if response.status_code == 200:
                print(f"  ¡ÉXITO! Este endpoint funciona")
                return True
                
        except Exception as e:
            print(f"Endpoint {endpoint}: ERROR - {e}")
    
    return False

def probar_envio_mensaje_con_metodos(api_key, email, server_url="https://127.0.0.1.nip.io"):
    """Probar enviar mensaje con diferentes métodos de autenticación"""
    
    payload = {
        "type": "stream",
        "to": "desarrollo",
        "topic": "channel events",
        "content": f"Mensaje de prueba - {datetime.now().strftime('%H:%M:%S')}"
    }
    
    print("\nProbando envío de mensajes con diferentes métodos:")
    
    # Método 1: HTTP Basic (API key como usuario)
    headers1 = {"Content-Type": "application/json"}
    auth1 = (api_key, "")
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers1,
            json=payload,
            auth=auth1,
            verify=False,
            timeout=10
        )
        print(f"POST Basic (key:user): {response.status_code}")
        if response.status_code == 200:
            print("  ¡ÉXITO! Mensaje enviado")
            return True
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"POST Basic (key:user): ERROR - {e}")
    
    # Método 2: HTTP Basic (email como usuario, API key como password)
    auth2 = (email, api_key)
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers1,
            json=payload,
            auth=auth2,
            verify=False,
            timeout=10
        )
        print(f"POST Basic (email:key): {response.status_code}")
        if response.status_code == 200:
            print("  ¡ÉXITO! Mensaje enviado")
            return True
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"POST Basic (email:key): ERROR - {e}")
    
    # Método 3: Bearer token
    headers3 = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(
            f"{server_url}/api/v1/messages",
            headers=headers3,
            json=payload,
            verify=False,
            timeout=10
        )
        print(f"POST Bearer: {response.status_code}")
        if response.status_code == 200:
            print("  ¡ÉXITO! Mensaje enviado")
            return True
        else:
            print(f"  Response: {response.text}")
    except Exception as e:
        print(f"POST Bearer: ERROR - {e}")
    
    return False

def main():
    """Función principal de diagnóstico"""
    
    print("=== DIAGNÓSTICO COMPLETO DE API KEYS ===")
    print("Investigando todas las posibles causas del error\n")
    
    # API keys
    zzz_key = "T4YKsnfXUDHFKzl5a3RAngwnhJHJnYRj"
    zzz_email = "zzz-bot@127.0.0.1.nip.io"
    xxx_key = "78VuC7SvAL9WtCN5zoHuaCeK9Ehf5yga"
    xxx_email = "xxx-bot@127.0.0.1.nip.io"
    
    server_url = "https://127.0.0.1.nip.io"
    
    print(f"Diagnóstico para zzz-bot ({zzz_email}):")
    print("=" * 50)
    
    # Probar diferentes métodos de autenticación
    print("1. Probando diferentes métodos de autenticación:")
    
    bearer_ok = probar_metodo_bearer(zzz_key, server_url)
    basic_ok = probar_metodo_basic(zzz_key, server_url)
    basic_email_ok = probar_metodo_basic_con_usuario(zzz_email, zzz_key, server_url)
    custom_ok = probar_metodo_header_custom(zzz_key, server_url)
    
    print(f"\nResultados autenticación:")
    print(f"  Bearer token: {'OK' if bearer_ok else 'ERROR'}")
    print(f"  HTTP Basic (key:user): {'OK' if basic_ok else 'ERROR'}")
    print(f"  HTTP Basic (email:key): {'OK' if basic_email_ok else 'ERROR'}")
    print(f"  X-API-Key header: {'OK' if custom_ok else 'ERROR'}")
    
    # Probar diferentes endpoints
    print("\n2. Probando diferentes endpoints:")
    endpoints_ok = probar_diferentes_endpoints(zzz_key, server_url)
    
    # Probar envío de mensajes
    print("\n3. Probando envío de mensajes:")
    mensaje_ok = probar_envio_mensaje_con_metodos(zzz_key, zzz_email, server_url)
    
    print("\n" + "=" * 50)
    print("RESUMEN DEL DIAGNÓSTICO:")
    print("=" * 50)
    
    if basic_email_ok or mensaje_ok:
        print("¡SOLUCIÓN ENCONTRADA!")
        if basic_email_ok:
            print("Usar: auth=(email, api_key)")
        if mensaje_ok:
            print("El envío de mensajes funciona con algún método")
        
        print("\nActualiza los scripts para usar el método correcto.")
    else:
        print("Ningún método funcionó. Posibles causas:")
        print("1. Las API keys no están activas en Zulip")
        print("2. Los bots no tienen permisos para enviar mensajes")
        print("3. Configuración adicional requerida en Zulip")
        print("4. Problema con la configuración del servidor")

if __name__ == "__main__":
    main()
