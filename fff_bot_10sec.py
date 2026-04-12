#!/usr/bin/env python3
"""
FFF-Bot envía mensajes cada 10 segundos usando Gemma2
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import random

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_message_every_10_seconds():
    """Enviar mensajes cada 10 segundos"""
    
    # Configuración del bot
    bot_email = "fff-bot@127.0.0.1.nip.io"
    api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
    server_url = "https://127.0.0.1.nip.io"
    ollama_url = "http://localhost:11434"
    
    headers = {"Content-Type": "application/json"}
    auth = (bot_email, api_key)
    
    # Canales para enviar mensajes
    channels = ["general", "noticias", "proyectos"]
    
    # Prompts para Gemma2
    prompts = [
        "Genera un mensaje corto y positivo para el equipo",
        "Comparte una idea interesante o curiosidad",
        "Dame un consejo útil o motivación",
        "Haz una pregunta reflexiva",
        "Comparte algo inspirador",
        "Genera un mensaje amigable y casual",
        "Dime algo interesante sobre tecnología",
        "Comparte un pensamiento positivo"
    ]
    
    print("=== FFF-BOT ENVIANDO MENSAJES CADA 10 SEGUNDOS ===")
    print("Presiona Ctrl+C para detener")
    print()
    
    message_count = 0
    
    try:
        while True:
            try:
                # Seleccionar canal y prompt aleatorio
                channel = random.choice(channels)
                prompt = random.choice(prompts)
                
                # Generar mensaje con Gemma2
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando mensaje...")
                
                gemma_payload = {
                    "model": "gemma2:2b",
                    "prompt": prompt,
                    "stream": False
                }
                
                gemma_response = requests.post(
                    f"{ollama_url}/api/generate",
                    json=gemma_payload,
                    timeout=30
                )
                
                if gemma_response.status_code == 200:
                    message_content = gemma_response.json().get("response", "")
                    
                    # Enviar a Zulip
                    zulip_payload = {
                        "type": "stream",
                        "to": channel,
                        "topic": "chat",
                        "content": f"{message_content}\n\n*FFF-Bot - {datetime.now().strftime('%H:%M:%S')}*"
                    }
                    
                    response = requests.post(
                        f"{server_url}/api/v1/messages",
                        headers=headers,
                        json=zulip_payload,
                        auth=auth,
                        verify=False,
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        message_count += 1
                        print(f"  Mensaje #{message_count} enviado a #{channel}")
                    else:
                        print(f"  Error: {response.status_code}")
                else:
                    print(f"  Error con Gemma2: {gemma_response.status_code}")
                
                # Esperar 10 segundos
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("\nDeteniendo...")
                break
            except Exception as e:
                print(f"  Error: {e}")
                time.sleep(10)
    
    except KeyboardInterrupt:
        print("\nPrograma detenido")
    
    print(f"\nTotal de mensajes enviados: {message_count}")

if __name__ == "__main__":
    send_message_every_10_seconds()
