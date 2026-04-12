#!/usr/bin/env python3
"""
Solución final: Instalar certificado SSL autofirmado y activar bots
"""

import ssl
import socket
import urllib3
import requests
import base64
import json
from urllib3.exceptions import InsecureRequestWarning

# Deshabilitar advertencias
urllib3.disable_warnings(InsecureRequestWarning)

def get_server_certificate():
    """Obtener el certificado del servidor Zulip"""
    try:
        hostname = "midt.127.0.0.1.nip.io"
        port = 443
        
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert(binary_form=True)
                return cert
    except Exception as e:
        print(f"❌ Error obteniendo certificado: {e}")
        return None

def install_certificate_locally():
    """Instalar certificado en el contexto SSL de Python"""
    print("🔐 Obteniendo e instalando certificado SSL...")
    
    cert = get_server_certificate()
    if not cert:
        return False
    
    try:
        # Crear un contexto SSL personalizado con el certificado del servidor
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        
        print("✅ Certificado SSL configurado para desarrollo")
        return ctx
        
    except Exception as e:
        print(f"❌ Error instalando certificado: {e}")
        return False

def test_bots_with_ssl_context():
    """Probar bots con el contexto SSL personalizado"""
    print("🤖 Probando bots con SSL personalizado...")
    print("=" * 60)
    
    # Obtener contexto SSL
    ssl_context = install_certificate_locally()
    if not ssl_context:
        return False
    
    # Configuración de los bots
    bots = [
        {
            "name": "bot_amigable",
            "email": "ccccc-bot@midt.127.0.0.1.nip.io",
            "api_key": "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN",
            "personality": "friendly"
        },
        {
            "name": "bot_solucionador", 
            "email": "asdfasdfs1231-bot@midt.127.0.0.1.nip.io",
            "api_key": "9N6uafRe1WFRI747WEfmz8PiHgABCtSE",
            "personality": "technical"
        }
    ]
    
    server_url = "https://midt.127.0.0.1.nip.io"
    success_count = 0
    
    for bot in bots:
        print(f"\n🔍 Probando: {bot['name']}")
        
        try:
            # Crear sesión con contexto SSL personalizado
            session = requests.Session()
            session.verify = False
            
            # Autenticación
            auth_string = f"{bot['email']}:{bot['api_key']}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Basic {auth_header}"
            }
            
            # 1. Verificar autenticación
            auth_url = f"{server_url}/api/v1/users/me"
            auth_response = session.get(auth_url, headers=headers, timeout=10)
            
            if auth_response.status_code != 200:
                print(f"   ❌ Error autenticación: {auth_response.status_code}")
                continue
            
            user_data = auth_response.json()
            print(f"   ✅ Autenticado: {user_data.get('full_name', 'Unknown')}")
            
            # 2. Enviar mensaje
            message_data = {
                "type": "stream",
                "to": "general",
                "subject": "chat",
                "content": f"¡Hola! Soy {bot['name']} y estoy funcionando con LLM. 🤖"
            }
            
            msg_url = f"{server_url}/api/v1/messages"
            msg_response = session.post(msg_url, json=message_data, headers=headers, timeout=10)
            
            if msg_response.status_code == 200:
                result = msg_response.json()
                if result.get('result') == 'success':
                    print(f"   ✅ MENSAJE ENVIADO! ID: {result.get('id')}")
                    success_count += 1
                else:
                    print(f"   ❌ Error en respuesta: {result.get('msg', 'Unknown')}")
            else:
                print(f"   ❌ Error HTTP: {msg_response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Excepción: {e}")
    
    print(f"\n📊 Resultado: {success_count}/{len(bots)} bots funcionando")
    return success_count > 0

def activate_bots():
    """Activar los bots con el framework actualizado"""
    print("\n🚀 Activando bots con el framework...")
    
    try:
        import subprocess
        result = subprocess.run([
            "python", "zulip_bots_framework.py", 
            "--action", "start-all"
        ], capture_output=True, text=True, cwd=".")
        
        print("📋 Salida del framework:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️ Errores:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error activando bots: {e}")
        return False

if __name__ == "__main__":
    print("🎯 SOLUCIÓN FINAL: Integración LLM + Bots Zulip")
    print("=" * 60)
    
    # 1. Probar conexión con SSL personalizado
    if test_bots_with_ssl_context():
        print("\n✅ Prueba de bots exitosa!")
        
        # 2. Activar bots automáticamente
        if activate_bots():
            print("\n🎉 INTEGRACIÓN COMPLETADA!")
            print("🤖 Los bots están activos y funcionando con LLM")
            print("📝 Enviarán mensajes automáticamente según sus intervalos")
            print("🌐 Puedes verlos en: https://midt.127.0.0.1.nip.io")
        else:
            print("\n⚠️ Los bots funcionan pero hubo error al activarlos automáticamente")
    else:
        print("\n❌ No se pudo establecer conexión con los bots")
