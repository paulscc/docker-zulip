#!/usr/bin/env python3
"""
Probar fff-bot Corregido
Probar el bot fff-bot con el formato correcto
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probar_fff_bot_corregido():
    """Probar fff-bot con el formato correcto"""
    
    print("=== PROBANDO FFF-BOT (CORREGIDO) ===")
    
    # Configuración del bot
    bot_email = "fff-bot@127.0.0.1.nip.io"
    bot_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    
    # Probar conexión
    print("1. Probando conexión...")
    headers = {
        "Content-Type": "application/json"
    }
    auth = (bot_email, bot_key)
    
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
            print(f"  Conexión exitosa: {user_data.get('full_name', 'Unknown')}")
            conexion_ok = True
        else:
            print(f"  Error de conexión: {response.status_code}")
            conexion_ok = False
            
    except Exception as e:
        print(f"  Error de conexión: {e}")
        conexion_ok = False
    
    if not conexion_ok:
        print("\nNo se puede conectar con fff-bot. Abortando.")
        return False
    
    # Probar diferentes formatos de payload
    print("\n2. Probando diferentes formatos de payload...")
    
    formatos_prueba = [
        {
            "nombre": "Formato estándar",
            "payload": {
                "type": "stream",
                "to": "desarrollo",
                "topic": "general",
                "content": "Mensaje de prueba desde fff-bot - Formato estándar"
            }
        },
        {
            "nombre": "Formato con stream",
            "payload": {
                "type": "stream",
                "stream": "desarrollo",
                "topic": "general", 
                "content": "Mensaje de prueba desde fff-bot - Formato con stream"
            }
        },
        {
            "nombre": "Formato simple",
            "payload": {
                "to": "desarrollo",
                "type": "stream",
                "content": "Mensaje de prueba desde fff-bot - Formato simple"
            }
        }
    ]
    
    for i, formato in enumerate(formatos_prueba, 1):
        print(f"\n  Probando {formato['nombre']}...")
        
        try:
            response = requests.post(
                f"{server_url}/api/v1/messages",
                headers=headers,
                json=formato['payload'],
                auth=auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"    ¡ÉXITO! {formato['nombre']} funciona")
                formato_exitoso = formato
                break
            else:
                print(f"    Error: {response.status_code}")
                print(f"    Response: {response.text}")
                
        except Exception as e:
            print(f"    Error: {e}")
    
    # Si encontramos un formato que funciona, enviar más mensajes
    if 'formato_exitoso' in locals():
        print(f"\n3. Enviando mensajes con formato exitoso...")
        
        canales = ["comercio", "desarrollo", "equipo", "general"]
        mensajes_enviados = 0
        
        for i, canal in enumerate(canales, 1):
            payload = formato_exitoso['payload'].copy()
            payload['to'] = canal
            payload['stream'] = canal
            payload['content'] = f"Mensaje de prueba #{i} en canal #{canal} desde fff-bot\n\n*Enviado a las {datetime.now().strftime('%H:%M:%S')}*"
            
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
                    mensajes_enviados += 1
                    print(f"  Mensaje {i} enviado exitosamente a #{canal}")
                else:
                    print(f"  Error mensaje {i}: {response.status_code}")
                
                time.sleep(1)
                
            except Exception as e:
                print(f"  Error mensaje {i}: {e}")
        
        print(f"\nTotal de mensajes enviados: {mensajes_enviados}/4")
        
        if mensajes_enviados > 0:
            print("\n¡ÉXITO! fff-bot funciona correctamente")
            print("Los mensajes deberían aparecer en los canales de Zulip")
            return True
        else:
            print("\nNo se pudieron enviar mensajes con fff-bot")
            return False
    else:
        print("\nNingún formato funcionó con fff-bot")
        return False

def main():
    """Función principal"""
    
    if probar_fff_bot_corregido():
        print("\n=== SIGUIENTES PASOS ===")
        print("1. fff-bot está funcionando correctamente")
        print("2. Los mensajes están apareciendo en Zulip")
        print("3. Ahora puedes activar el sistema completo:")
        print("   - Inicia: python publicador_multibot.py")
        print("   - Envía más mensajes con fff-bot")
        print("   - Verás resúmenes automáticos")
    else:
        print("\nfff-bot no funciona. Revisa la configuración.")

if __name__ == "__main__":
    main()
