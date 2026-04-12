#!/usr/bin/env python3
"""
Multi-Bot - Todos los bots genéricos envían mensajes cada 10 segundos usando Gemma2
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import random
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class MultiBotSystem:
    def __init__(self):
        """Inicializar sistema multi-bot"""
        self.ollama_url = "http://localhost:11434"
        self.model = "gemma2:2b"
        
        # Configuración de todos los bots genéricos
        self.bots = [
            {
                "name": "bbbbb-bot",
                "email": "bbbbb-bot@midt.127.0.0.1.nip.io",
                "api_key": "nUf4sYDfwZQCR7xdBbFS9hCw3KXMsQhv",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general"],
                "start_delay": 0
            },
            {
                "name": "nnnnn-bot", 
                "email": "nnnnn-bot@midt.127.0.0.1.nip.io",
                "api_key": "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general", "noticias"],
                "start_delay": 1
            },
            {
                "name": "aaaaa-bot",
                "email": "aaaaa-bot@midt.127.0.0.1.nip.io", 
                "api_key": "Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "casual",
                "channels": ["general", "proyectos"],
                "start_delay": 2
            },
            {
                "name": "tt-bot",
                "email": "tt-bot@midt.127.0.0.1.nip.io",
                "api_key": "HwVy87Cag8cd9sXgNln0D8VuLmrICyog", 
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "technical",
                "channels": ["desarrollo", "proyectos"],
                "start_delay": 3
            },
            {
                "name": "yy-bot",
                "email": "yy-bot@midt.127.0.0.1.nip.io",
                "api_key": "AMSLtR84HEG9XeWD820xGsI9W49emFag",
                "server_url": "https://midt.127.0.0.1.nip.io", 
                "personality": "friendly",
                "channels": ["noticias", "general"],
                "start_delay": 4
            },
            {
                "name": "uu-bot",
                "email": "uu-bot@midt.127.0.0.1.nip.io",
                "api_key": "5SsIvvAbUDPqkd9O3V8kG0UICZLm5jH7",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "professional", 
                "channels": ["desarrollo", "proyectos"],
                "start_delay": 5
            },
            {
                "name": "ii-bot",
                "email": "ii-bot@midt.127.0.0.1.nip.io",
                "api_key": "VZXtdmZ66e0alod7SdO9sh31jvtRVblS",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "casual",
                "channels": ["noticias", "proyectos"], 
                "start_delay": 6
            },
            {
                "name": "yyyyy-bot",
                "email": "yyyyy-bot@midt.127.0.0.1.nip.io",
                "api_key": "X6r9KIOZMEcaACvFDmeiRDqMuPswmZby",
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general", "proyectos"],
                "start_delay": 7
            },
            {
                "name": "ffff-bot",
                "email": "ffff-bot@midt.127.0.0.1.nip.io",
                "api_key": "XDsjiG1rUAKO3ZR9nsyNvCODlRWnjpQb", 
                "server_url": "https://midt.127.0.0.1.nip.io",
                "personality": "technical",
                "channels": ["desarrollo", "noticias"],
                "start_delay": 8
            }
        ]
        
        self.running = True
        self.message_counts = {bot["name"]: 0 for bot in self.bots}
        self.error_counts = {bot["name"]: 0 for bot in self.bots}
    
    def get_prompt_for_personality(self, personality):
        """Obtener prompt según la personalidad del bot"""
        prompts = {
            "friendly": [
                "Genera un mensaje corto y positivo para el equipo",
                "Comparte algo amigable y motivador",
                "Dime algo bueno para animar al grupo",
                "Hola equipo, ¿cómo están todos?",
                "Comparte un pensamiento positivo y alentador"
            ],
            "casual": [
                "Genera un mensaje casual y relajado para el chat",
                "Comente algo interesante de forma informal",
                "Qué tal si compartimos algo divertido",
                "Alguien tiene algo chistoso que contar",
                "Hablemos de algo relajado y amigable"
            ],
            "technical": [
                "Comparte un dato técnico interesante",
                "Genera un consejo útil sobre desarrollo",
                "Dime algo sobre tecnología o código",
                "Comparte una perspectiva técnica",
                "Hablemos de innovación y desarrollo"
            ],
            "professional": [
                "Genera un mensaje profesional y constructivo",
                "Comparte una idea de mejora para el equipo",
                "Dime algo sobre productividad o trabajo",
                "Comparte una perspectiva profesional",
                "Hablemos de crecimiento y desarrollo"
            ]
        }
        return random.choice(prompts.get(personality, prompts["friendly"]))
    
    def generate_message_with_gemma2(self, prompt, personality):
        """Generar mensaje usando Gemma2"""
        try:
            # Agregar contexto de personalidad
            personality_context = {
                "friendly": "Eres un bot amigable y positivo. ",
                "casual": "Eres un bot casual y relajado. ",
                "technical": "Eres un bot técnico y experto. ",
                "professional": "Eres un bot profesional y formal. "
            }
            
            full_prompt = personality_context.get(personality, "") + prompt
            
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                return f"Error Gemma2: {response.status_code}"
                
        except Exception as e:
            return f"Error: {e}"
    
    def send_message_to_zulip(self, bot, channel, content):
        """Enviar mensaje a Zulip usando form-data"""
        try:
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
            
            return response.status_code == 200
            
        except Exception as e:
            print(f"  Error enviando mensaje: {e}")
            return False
    
    def run_bot(self, bot):
        """Ejecutar un bot individual"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']} iniciando...")
        
        # Esperar el delay inicial
        time.sleep(bot["start_delay"])
        
        while self.running:
            try:
                # Seleccionar canal aleatorio
                channel = random.choice(bot["channels"])
                
                # Generar prompt según personalidad
                prompt = self.get_prompt_for_personality(bot["personality"])
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']} generando mensaje para #{channel}...")
                
                # Generar mensaje con Gemma2
                message_content = self.generate_message_with_gemma2(prompt, bot["personality"])
                
                if message_content and not message_content.startswith("Error"):
                    # Enviar a Zulip
                    if self.send_message_to_zulip(bot, channel, message_content):
                        self.message_counts[bot["name"]] += 1
                        print(f"  {bot['name']}: Mensaje #{self.message_counts[bot['name']]} enviado a #{channel}")
                    else:
                        self.error_counts[bot["name"]] += 1
                        print(f"  {bot['name']}: Error al enviar mensaje")
                else:
                    self.error_counts[bot["name"]] += 1
                    print(f"  {bot['name']}: {message_content}")
                
                # Esperar 10 segundos
                time.sleep(10)
                
            except KeyboardInterrupt:
                print(f"\n{bot['name']} deteniendo...")
                break
            except Exception as e:
                self.error_counts[bot["name"]] += 1
                print(f"  {bot['name']}: Error inesperado - {e}")
                time.sleep(10)
    
    def start_all_bots(self):
        """Iniciar todos los bots simultáneamente"""
        print("=== SISTEMA MULTI-BOT - TODOS LOS BOTS CADA 10 SEGUNDOS ===")
        print(f"Bots activos: {len(self.bots)}")
        print(f"Modelo: {self.model}")
        print("Presiona Ctrl+C para detener todos los bots")
        print()
        
        # Crear threads para cada bot
        threads = []
        for bot in self.bots:
            thread = threading.Thread(target=self.run_bot, args=(bot,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        try:
            # Mostrar estadísticas cada 30 segundos
            while self.running:
                time.sleep(30)
                self.show_stats()
                
        except KeyboardInterrupt:
            print("\nDeteniendo todos los bots...")
            self.running = False
            
            # Esperar que todos los threads terminen
            for thread in threads:
                thread.join(timeout=5)
            
            self.show_final_stats()
    
    def show_stats(self):
        """Mostrar estadísticas actuales"""
        print(f"\n=== ESTADÍSTICAS - {datetime.now().strftime('%H:%M:%S')} ===")
        total_messages = sum(self.message_counts.values())
        total_errors = sum(self.error_counts.values())
        
        print(f"Total mensajes: {total_messages} | Total errores: {total_errors}")
        
        for bot in self.bots:
            count = self.message_counts[bot["name"]]
            errors = self.error_counts[bot["name"]]
            print(f"  {bot['name']}: {count} mensajes, {errors} errores")
        
        print()
    
    def show_final_stats(self):
        """Mostrar estadísticas finales"""
        print("\n=== ESTADÍSTICAS FINALES ===")
        total_messages = sum(self.message_counts.values())
        total_errors = sum(self.error_counts.values())
        
        print(f"Total mensajes enviados: {total_messages}")
        print(f"Total errores: {total_errors}")
        print(f"Tasa de éxito: {(total_messages/(total_messages+total_errors)*100):.1f}%" if (total_messages + total_errors) > 0 else "N/A")
        
        print("\nPor bot:")
        for bot in self.bots:
            count = self.message_counts[bot["name"]]
            errors = self.error_counts[bot["name"]]
            print(f"  {bot['name']}: {count} mensajes, {errors} errores")

def main():
    """Función principal"""
    system = MultiBotSystem()
    system.start_all_bots()

if __name__ == "__main__":
    main()
