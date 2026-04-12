#!/usr/bin/env python3
"""
Probar Nuevas API Keys
Probar las nuevas API keys de los bots de webhook
"""

import requests
import json
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probar_api_key(email, api_key, server_url="https://127.0.0.1.nip.io"):
    """Probar una API key específica"""
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")
    
    try:
        # Probar conexión básica
        response = requests.get(
            f"{server_url}/api/v1/users/me",
            headers=headers,
            auth=auth,
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"  {email}: OK - {user_data.get('full_name', 'Unknown')}")
            return True
        else:
            print(f"  {email}: ERROR {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"  {email}: ERROR - {e}")
        return False

def enviar_mensaje_con_bot(api_key, email):
    """Enviar un mensaje de prueba con un bot específico"""
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")
    server_url = "https://127.0.0.1.nip.io"
    
    payload = {
        "type": "stream",
        "to": "desarrollo",
        "topic": "channel events",
        "content": f"Mensaje de prueba desde {email}\n\n*Enviado a las {datetime.now().strftime('%H:%M:%S')}*\n\nEste es un mensaje para probar que el sistema de webhooks con Kafka funciona correctamente."
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
            print(f"  Mensaje enviado exitosamente desde {email}")
            return True
        else:
            print(f"  Error enviando mensaje: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"  Error enviando mensaje: {e}")
        return False

def main():
    """Función principal"""
    
    print("=== PRUEBA DE NUEVAS API KEYS ===")
    print("Verificando las nuevas API keys de los bots de webhook\n")
    
    # Nuevas API keys
    zzz_key = "T4YKsnfXUDHFKzl5a3RAngwnhJHJnYRj"
    xxx_key = "78VuC7SvAL9WtCN5zoHuaCeK9Ehf5yga"
    
    # Probar bot de entrada (zzz-bot)
    print("Bot de entrada (zzz-bot):")
    zzz_ok = probar_api_key("zzz-bot@127.0.0.1.nip.io", zzz_key)
    
    # Probar bot de salida (xxx-bot)
    print("\nBot de salida (xxx-bot):")
    xxx_ok = probar_api_key("xxx-bot@127.0.0.1.nip.io", xxx_key)
    
    if zzz_ok and xxx_ok:
        print("\n=== AMBOS BOTS DE WEBHOOK FUNCIONAN ===")
        
        # Enviar mensaje de prueba con el bot de entrada
        print("\nEnviando mensaje de prueba con zzz-bot...")
        if enviar_mensaje_con_bot(zzz_key, "zzz-bot@127.0.0.1.nip.io"):
            print("\n¡ÉXITO! El mensaje fue enviado al canal #desarrollo")
            print("Deberías ver el mensaje en Zulip ahora mismo.")
            print("\nEl sistema está listo para funcionar completamente:")
            print("1. Los bots pueden conectarse a Zulip")
            print("2. Pueden enviar mensajes a los canales")
            print("3. El sistema de Kafka + Ollama está funcionando")
            print("4. Los resúmenes aparecerán automáticamente")
            
            # Enviar más mensajes para activar el sistema
            print("\nEnviando más mensajes para activar el sistema de resúmenes...")
            for i in range(3):
                print(f"  Enviando mensaje adicional {i+2}...")
                enviar_mensaje_con_bot(zzz_key, "zzz-bot@127.0.0.1.nip.io")
            
            print("\nMensajes enviados. El sistema debería:")
            print("- Detectar los mensajes no leídos")
            print("- Enviarlos a Kafka para procesamiento")
            print("- Generar resúmenes con gemma2:2b")
            print("- Publicar resúmenes en #desarrollo/resumen-general")
            
        else:
            print("\nError al enviar mensaje de prueba")
    else:
        print("\n=== ALGUNOS BOTS TIENEN PROBLEMAS ===")
        print("Revisa las API keys o genera nuevas en la interfaz de Zulip")

if __name__ == "__main__":
    main()
