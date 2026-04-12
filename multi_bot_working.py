#!/usr/bin/env python3
"""
Multi-Bot Working - Solo bots que sabemos que funcionan
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import random

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def run_multi_bot_working():
    """Ejecutar múltiples bots que sabemos que funcionan"""
    
    # Solo usar el bot fff-bot que ya probamos que funciona
    bots = [
        {
            "name": "fff-bot",
            "email": "fff-bot@127.0.0.1.nip.io",
            "api_key": "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv",
            "server_url": "https://127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
        }
    ]
    
    # Si quieres agregar más bots, agrégalos aquí con sus credenciales correctas
    # Por ejemplo:
    # {
    #     "name": "otro-bot",
    #     "email": "otro-bot@127.0.0.1.nip.io", 
    #     "api_key": "API_KEY_CORRECTA",
    #     "server_url": "https://127.0.0.1.nip.io",
    #     "personality": "casual",
    #     "channels": ["general"]
    # }
    
    print("=== MULTI-BOT WORKING ===")
    print(f"Bots activos: {len(bots)}")
    print("Presiona Ctrl+C para detener")
    print()
    
    message_counts = {bot["name"]: 0 for bot in bots}
    error_counts = {bot["name"]: 0 for bot in bots}
    
    def get_prompt(personality):
        prompts = {
            "friendly": [
                "Genera un mensaje corto y positivo para el equipo",
                "Hola equipo, ¿cómo están todos?",
                "Comparte algo bueno y motivador",
                "Buen día a todos, ¿qué tal?",
                "Saludos equipo, sigamos con energía"
            ],
            "casual": [
                "Genera un mensaje casual y relajado",
                "Qué onda equipo, ¿qué hay de nuevo?",
                "Buenas, alguien tiene algo interesante?",
                "Hey equipo, ¿cómo va todo?",
                "Qué tal si compartimos algo divertido"
            ],
            "technical": [
                "Comparte un dato técnico interesante",
                "Genera un consejo útil sobre desarrollo",
                "Alguna novedad tecnológica interesante?",
                "Tips de código para el equipo",
                "Qué tal si hablamos de innovación"
            ]
        }
        return random.choice(prompts.get(personality, prompts["friendly"]))
    
    def generate_message_gemma2(prompt, personality):
        try:
            personality_context = {
                "friendly": "Eres un bot amigable y positivo. ",
                "casual": "Eres un bot casual y relajado. ",
                "technical": "Eres un bot técnico y experto. "
            }
            
            full_prompt = personality_context.get(personality, "") + prompt + " (máximo 2 líneas)"
            
            payload = {
                "model": "gemma2:2b",
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(
                "http://localhost:11434/api/generate",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return None
                
        except Exception as e:
            print(f"    Error Gemma2: {e}")
            return None
    
    def send_message(bot, content):
        try:
            channel = random.choice(bot["channels"])
            auth = (bot["email"], bot["api_key"])
            
            data = {
                "type": "stream",
                "to": channel,
                "topic": "chat",
                "content": f"{content}\n\n*{bot['name']} con Gemma2 - {datetime.now().strftime('%H:%M:%S')}*"
            }
            
            response = requests.post(
                f"{bot['server_url']}/api/v1/messages",
                data=data,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            return response.status_code == 200, channel
            
        except Exception as e:
            print(f"    Error Zulip: {e}")
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
                user_data = response.json()
                print(f"  {bot['name']}: OK ({user_data.get('full_name', 'Unknown')})")
            else:
                print(f"  {bot['name']}: ERROR - {response.status_code}")
                print(f"    Response: {response.text}")
                return
        except Exception as e:
            print(f"  {bot['name']}: ERROR - {e}")
            return
    
    print("Todas las conexiones OK!")
    print("Iniciando envío de mensajes cada 10 segundos...")
    print()
    
    try:
        while True:
            for bot in bots:
                try:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}...")
                    
                    # Generar mensaje
                    prompt = get_prompt(bot["personality"])
                    message = generate_message_gemma2(prompt, bot["personality"])
                    
                    if message and not message.startswith("Error"):
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
                        print(f"  Error: {message}")
                    
                    # Esperar 10 segundos antes del siguiente bot
                    time.sleep(10)
                    
                except Exception as e:
                    error_counts[bot["name"]] += 1
                    print(f"  Error inesperado: {e}")
                    time.sleep(10)
            
            # Mostrar estadísticas cada ronda
            total_messages = sum(message_counts.values())
            total_errors = sum(error_counts.values())
            print(f"--- Estadísticas: {total_messages} mensajes, {total_errors} errores ---")
            print()
            
    except KeyboardInterrupt:
        print("\nDeteniendo...")
    
    # Estadísticas finales
    print("\n=== ESTADÍSTICAS FINALES ===")
    total_messages = sum(message_counts.values())
    total_errors = sum(error_counts.values())
    print(f"Total mensajes enviados: {total_messages}")
    print(f"Total errores: {total_errors}")
    if (total_messages + total_errors) > 0:
        print(f"Tasa de éxito: {(total_messages/(total_messages+total_errors))*100:.1f}%")
    
    for bot in bots:
        print(f"  {bot['name']}: {message_counts[bot['name']]} mensajes, {error_counts[bot['name']]} errores")

if __name__ == "__main__":
    run_multi_bot_working()
