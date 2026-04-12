#!/usr/bin/env python3
"""
Multi-Bot Simple - Versión reducida y sincronizada
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import random

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_multi_bot_simple():
    """Ejecutar múltiples bots de forma secuencial y sincronizada"""
    
    # Configuración de bots (reducidos para no sobrecargar)
    bots = [
        {
            "name": "bbbbb-bot",
            "email": "bbbbb-bot@midt.127.0.0.1.nip.io",
            "api_key": "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": ["general"]
        },
        {
            "name": "nnnnn-bot", 
            "email": "nnnnn-bot@midt.127.0.0.1.nip.io",
            "api_key": "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": ["general", "noticias"]
        },
        {
            "name": "aaaaa-bot",
            "email": "aaaaa-bot@midt.127.0.0.1.nip.io", 
            "api_key": "Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "casual",
            "channels": ["general", "proyectos"]
        },
        {
            "name": "tt-bot",
            "email": "tt-bot@midt.127.0.0.1.nip.io",
            "api_key": "HwVy87Cag8cd9sXgNln0D8VuLmrICyog", 
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "technical",
            "channels": ["desarrollo", "proyectos"]
        },
        {
            "name": "yy-bot",
            "email": "yy-bot@midt.127.0.0.1.nip.io",
            "api_key": "AMSLtR84HEG9XeWD820xGsI9W49emFag",
            "server_url": "https://midt.127.0.0.1.nip.io", 
            "personality": "friendly",
            "channels": ["noticias", "general"]
        }
    ]
    
    print("=== MULTI-BOT SIMPLE - 5 BOTS CADA 10 SEGUNDOS ===")
    print("Presiona Ctrl+C para detener")
    print()
    
    message_counts = {bot["name"]: 0 for bot in bots}
    error_counts = {bot["name"]: 0 for bot in bots}
    
    def get_prompt(personality):
        prompts = {
            "friendly": ["Hola equipo", "Buen día a todos", "¿Cómo están?", "Saludos", "Qué tal"],
            "casual": ["Qué onda", "Buenas", "¿Qué hay de nuevo?", "Hey equipo", "Qué tal todo"],
            "technical": ["Alguna actualización técnica", "Novedades de desarrollo", "Tips de código", "Tech update", "Dev news"]
        }
        return random.choice(prompts.get(personality, prompts["friendly"]))
    
    def generate_message_gemma2(prompt, personality):
        try:
            personality_context = {
                "friendly": "Eres amigable y positivo. ",
                "casual": "Eres casual y relajado. ",
                "technical": "Eres técnico y experto. "
            }
            
            full_prompt = personality_context.get(personality, "") + prompt + " (responde muy corto)"
            
            payload = {
                "model": "gemma2:2b",
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return None
                
        except Exception:
            return None
    
    def send_message(bot, content):
        try:
            channel = random.choice(bot["channels"])
            auth = (bot["email"], bot["api_key"])
            
            data = {
                "type": "stream",
                "to": channel,
                "topic": "chat",
                "content": f"{content}\n\n*{bot['name']} - {datetime.now().strftime('%H:%M:%S')}*"
            }
            
            response = requests.post(
                f"{bot['server_url']}/api/v1/messages",
                data=data,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            return response.status_code == 200, channel
            
        except Exception:
            return False, None
    
    # Probar conexión de todos los bots primero
    print("Verificando conexiones...")
    for bot in bots:
        try:
            auth = (bot["email"], bot["api_key"])
            response = requests.get(
                f"{bot['server_url']}/api/v1/users/me",
                auth=auth,
                verify=False,
                timeout=10
            )
            if response.status_code == 200:
                print(f"  {bot['name']}: OK")
            else:
                print(f"  {bot['name']}: ERROR - {response.status_code}")
                return
        except Exception as e:
            print(f"  {bot['name']}: ERROR - {e}")
            return
    
    print("Todas las conexiones OK!")
    print("Iniciando envío de mensajes...")
    print()
    
    try:
        round_count = 0
        
        while True:
            round_count += 1
            print(f"=== RONDA {round_count} - {datetime.now().strftime('%H:%M:%S')} ===")
            
            # Procesar cada bot secuencialmente
            for bot in bots:
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}...")
                    
                    # Generar mensaje
                    prompt = get_prompt(bot["personality"])
                    message = generate_message_gemma2(prompt, bot["personality"])
                    
                    if message:
                        # Enviar mensaje
                        success, channel = send_message(bot, message)
                        
                        if success:
                            message_counts[bot["name"]] += 1
                            print(f"  Mensaje #{message_counts[bot['name']]} enviado a #{channel}")
                        else:
                            error_counts[bot["name"]] += 1
                            print(f"  Error al enviar mensaje")
                    else:
                        error_counts[bot["name"]] += 1
                        print(f"  Error generando mensaje")
                    
                    # Pequeña pausa entre bots
                    time.sleep(2)
                    
                except Exception as e:
                    error_counts[bot["name"]] += 1
                    print(f"  Error: {e}")
                    time.sleep(2)
            
            # Mostrar resumen de la ronda
            total_messages = sum(message_counts.values())
            total_errors = sum(error_counts.values())
            print(f"  Resumen ronda: {total_messages} mensajes totales, {total_errors} errores")
            print()
            
            # Esperar 10 segundos antes de la siguiente ronda
            time.sleep(10)
            
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    
    # Estadísticas finales
    print("\n=== ESTADÍSTICAS FINALES ===")
    total_messages = sum(message_counts.values())
    total_errors = sum(error_counts.values())
    print(f"Total mensajes: {total_messages}")
    print(f"Total errores: {total_errors}")
    print(f"Rondas completadas: {round_count}")
    
    for bot in bots:
        print(f"  {bot['name']}: {message_counts[bot['name']]} mensajes, {error_counts[bot['name']]} errores")

if __name__ == "__main__":
    run_multi_bot_simple()
