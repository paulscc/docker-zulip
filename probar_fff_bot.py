#!/usr/bin/env python3
"""
Probar fff-bot
Probar el bot fff-bot con la API key proporcionada
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probar_fff_bot():
    """Probar la conexión y envío de mensajes con fff-bot"""
    
    print("=== PROBANDO FFF-BOT ===")
    print(f"Email: fff-bot@127.0.0.1.nip.io")
    print(f"API Key: WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv")
    print(f"Server: https://127.0.0.1.nip.io\n")
    
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
            print(f"  Response: {response.text}")
            conexion_ok = False
            
    except Exception as e:
        print(f"  Error de conexión: {e}")
        conexion_ok = False
    
    if not conexion_ok:
        print("\nNo se puede conectar con fff-bot. Abortando.")
        return False
    
    # Probar envío de mensajes
    print("\n2. Enviando mensajes de prueba...")
    
    mensajes_prueba = [
        {"canal": "comercio", "contenido": "Prueba de mensaje en canal comercio desde fff-bot"},
        {"canal": "desarrollo", "contenido": "Prueba de mensaje en canal desarrollo desde fff-bot"},
        {"canal": "equipo", "contenido": "Prueba de mensaje en canal equipo desde fff-bot"},
        {"canal": "general", "contenido": "Prueba de mensaje en canal general desde fff-bot"}
    ]
    
    mensajes_enviados = 0
    
    for i, msg in enumerate(mensajes_prueba, 1):
        payload = {
            "type": "stream",
            "to": msg["canal"],
            "topic": "general",
            "content": f"{msg['contenido']}\n\n*Mensaje de prueba #{i} - {datetime.now().strftime('%H:%M:%S')}*"
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
                mensajes_enviados += 1
                print(f"  Mensaje {i} enviado exitosamente a #{msg['canal']}")
            else:
                print(f"  Error mensaje {i}: {response.status_code}")
                print(f"  Response: {response.text}")
            
            time.sleep(1)  # Pequeña pausa entre mensajes
            
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

def main():
    """Función principal"""
    
    if probar_fff_bot():
        print("\n=== SIGUIENTES PASOS ===")
        print("1. fff-bot está funcionando correctamente")
        print("2. Ahora puedes usar fff-bot para llenar los canales")
        print("3. Inicia el publicador multi-bot:")
        print("   python publicador_multibot.py")
        print("4. fff-bot enviará mensajes automáticamente")
        print("5. El sistema generará resúmenes automáticos")
    else:
        print("\nfff-bot no funciona. Revisa la configuración.")

if __name__ == "__main__":
    main()
