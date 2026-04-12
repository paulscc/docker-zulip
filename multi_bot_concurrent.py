#!/usr/bin/env python3
"""
Multi-Bot Concurrent - Todos los bots operan independientemente cada 10 segundos
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import random
import threading
import queue
from concurrent.futures import ThreadPoolExecutor

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class ConcurrentMultiBotSystem:
    def __init__(self):
        """Inicializar sistema multi-bot concurrente"""
        self.ollama_url = "http://localhost:11434"
        self.model = "gemma2:2b"
        self.running = True
        
        # Lista de bots verificados
        self.bots = [
            {
                "name": "fff-bot",
                "email": "fff-bot@127.0.0.1.nip.io",
                "api_key": "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "aaa-bot",
                "email": "aaa-bot@127.0.0.1.nip.io",
                "api_key": "f68mFE6Ihur5eNW58V2b3jE7cPvqOsWw",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "casual",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "bbb-bot",
                "email": "bbb-bot@127.0.0.1.nip.io",
                "api_key": "39EB0ERDtAEPi63lMP77aEQ9NrUI2fp4",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "technical",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "ddd-bot",
                "email": "ddd-bot@127.0.0.1.nip.io",
                "api_key": "WqEhRLLFVBktfSjGdquLIJ84b52q3VB8",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "eee-bot",
                "email": "eee-bot@127.0.0.1.nip.io",
                "api_key": "KKONeQT2YEC6q2fwENt0vSqwzrkDUmbT",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "professional",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "ggg-bot",
                "email": "ggg-bot@127.0.0.1.nip.io",
                "api_key": "l71o3mHodGNViO3DEpQFYUKTKHA1PQsk",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "technical",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "hhh-bot",
                "email": "hhh-bot@127.0.0.1.nip.io",
                "api_key": "lgCtjcfOlY4s2vVXRuBKDRszr4YlyJ8t",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "casual",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "iii-bot",
                "email": "iii-bot@127.0.0.1.nip.io",
                "api_key": "oNhze1f1pF7mWWfLsLllSU6qCX3pgnJ6",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "casual",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "jjj-bot",
                "email": "jjj-bot@127.0.0.1.nip.io",
                "api_key": "xCr4tCZdbBUhPSjX594fOkt6U4a6qaRT",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "technical",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            },
            {
                "name": "kkk-bot",
                "email": "kkk-bot@127.0.0.1.nip.io",
                "api_key": "j23GPTvEPcbUw5dtqqy2gKAkEI8c3lvJ",
                "server_url": "https://127.0.0.1.nip.io",
                "personality": "friendly",
                "channels": ["general", "desarrollo", "comercio", "equipo", "sandbox", "Zulip"]
            }
        ]
        
        # Estadísticas compartidas con locks para thread safety
        self.message_counts = {bot["name"]: 0 for bot in self.bots}
        self.error_counts = {bot["name"]: 0 for bot in self.bots}
        self.stats_lock = threading.Lock()
        
        # Cola para solicitudes a Gemma2 (para evitar sobrecarga)
        self.gemma_queue = queue.Queue(maxsize=20)
    
    def get_prompt_for_personality(self, personality):
        """Obtener prompt según la personalidad del bot"""
        prompts = {
            "friendly": [
                "Genera un mensaje corto y positivo para el equipo",
                "Hola equipo, ¿cómo están todos?",
                "Comparte algo bueno y motivador",
                "Buen día a todos, ¿qué tal?",
                "Saludos equipo, sigamos con energía",
                "Qué tal si animamos el grupo con algo positivo",
                "Alguien tiene buenas noticias que compartir?",
                "Sigamos trabajando con buena actitud"
            ],
            "casual": [
                "Genera un mensaje casual y relajado",
                "Qué onda equipo, ¿qué hay de nuevo?",
                "Buenas, alguien tiene algo interesante?",
                "Hey equipo, ¿cómo va todo?",
                "Qué tal si compartimos algo divertido",
                "Alguien quiere conversar de algo informal?",
                "Buen día, ¿qué les parece si charlamos un rato?",
                "Qué tal el día de todos hoy?"
            ],
            "technical": [
                "Comparte un dato técnico interesante",
                "Genera un consejo útil sobre desarrollo",
                "Alguna novedad tecnológica interesante?",
                "Tips de código para el equipo",
                "Qué tal si hablamos de innovación",
                "Alguien descubrió algo técnico útil?",
                "Compartamos conocimientos técnicos",
                "Qué tal si discutimos sobre tecnología"
            ],
            "professional": [
                "Genera un mensaje profesional y constructivo",
                "Comparte una idea de mejora para el equipo",
                "Dime algo sobre productividad o trabajo",
                "Comparte una perspectiva profesional",
                "Hablemos de crecimiento y desarrollo",
                "Alguna sugerencia para mejorar nuestro trabajo?",
                "Qué tal si establecemos metas profesionales",
                "Compartamos buenas prácticas laborales"
            ]
        }
        return random.choice(prompts.get(personality, prompts["friendly"]))
    
    def generate_message_with_gemma2(self, prompt, personality):
        """Generar mensaje usando Gemma2 con reintentos"""
        max_retries = 3
        for attempt in range(max_retries):
            try:
                personality_context = {
                    "friendly": "Eres un bot amigable y positivo. ",
                    "casual": "Eres un bot casual y relajado. ",
                    "technical": "Eres un bot técnico y experto. ",
                    "professional": "Eres un bot profesional y formal. "
                }
                
                full_prompt = personality_context.get(personality, "") + prompt + " (máximo 2 líneas)"
                
                payload = {
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False
                }
                
                response = requests.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result.get("response", "").strip()
                else:
                    if attempt < max_retries - 1:
                        time.sleep(1)  # Esperar antes de reintentar
                    continue
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(1)  # Esperar antes de reintentar
                continue
        
        return None
    
    def send_message_to_zulip(self, bot, content):
        """Enviar mensaje a Zulip usando form-data"""
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
            return False, None
    
    def run_bot_independently(self, bot):
        """Ejecutar un bot de forma independiente cada 10 segundos"""
        # Inicio aleatorio entre 0-10 segundos
        random_start = random.uniform(0, 10)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']} iniciando en {random_start:.1f}s...")
        time.sleep(random_start)
        
        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']} INICIADO - enviando mensajes cada 10s")
        
        while self.running:
            try:
                start_time = time.time()
                
                # Generar mensaje
                prompt = self.get_prompt_for_personality(bot["personality"])
                message = self.generate_message_with_gemma2(prompt, bot["personality"])
                
                if message and not message.startswith("Error"):
                    # Enviar mensaje
                    success, channel = self.send_message_to_zulip(bot, message)
                    
                    with self.stats_lock:
                        if success:
                            self.message_counts[bot["name"]] += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}: Mensaje #{self.message_counts[bot['name']]} a #{channel}")
                        else:
                            self.error_counts[bot["name"]] += 1
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}: Error al enviar mensaje")
                else:
                    with self.stats_lock:
                        self.error_counts[bot["name"]] += 1
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}: Error generando mensaje")
                
                # Calcular tiempo restante para mantener intervalo de 10 segundos
                elapsed = time.time() - start_time
                remaining_time = max(0, 10 - elapsed)
                
                if remaining_time > 0:
                    time.sleep(remaining_time)
                
            except KeyboardInterrupt:
                print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {bot['name']} deteniendo...")
                break
            except Exception as e:
                with self.stats_lock:
                    self.error_counts[bot["name"]] += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot['name']}: Error inesperado - {e}")
                time.sleep(10)
    
    def test_all_connections(self):
        """Probar conexión de todos los bots"""
        print("Verificando conexiones...")
        connected_bots = []
        
        for bot in self.bots:
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
                    connected_bots.append(bot)
                else:
                    print(f"  {bot['name']}: ERROR - {response.status_code}")
                    with self.stats_lock:
                        self.error_counts[bot["name"]] += 1
            except Exception as e:
                print(f"  {bot['name']}: ERROR - {e}")
                with self.stats_lock:
                    self.error_counts[bot["name"]] += 1
        
        return connected_bots
    
    def show_stats(self):
        """Mostrar estadísticas actuales"""
        with self.stats_lock:
            total_messages = sum(self.message_counts.values())
            total_errors = sum(self.error_counts.values())
            
            print(f"\n=== ESTADÍSTICAS - {datetime.now().strftime('%H:%M:%S')} ===")
            print(f"Total mensajes: {total_messages} | Total errores: {total_errors}")
            
            for bot in self.bots:
                count = self.message_counts[bot["name"]]
                errors = self.error_counts[bot["name"]]
                print(f"  {bot['name']}: {count} mensajes, {errors} errores")
            
            print()
    
    def start_all_bots(self):
        """Iniciar todos los bots simultáneamente"""
        print("=== MULTI-BOT CONCURRENT - TODOS LOS BOTS CADA 10 SEGUNDOS ===")
        print(f"Bots activos: {len(self.bots)}")
        print("Cada bot opera independientemente con inicio aleatorio")
        print("Presiona Ctrl+C para detener todos los bots")
        print()
        
        # Probar conexiones
        connected_bots = self.test_all_connections()
        
        if not connected_bots:
            print("No se pudo conectar con ningún bot. Abortando.")
            return
        
        print(f"\nConectados {len(connected_bots)}/{len(self.bots)} bots")
        print("Iniciando todos los bots concurrentemente...")
        print()
        
        # Crear threads para cada bot
        threads = []
        for bot in connected_bots:
            thread = threading.Thread(target=self.run_bot_independently, args=(bot,))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        # Thread para mostrar estadísticas
        def stats_thread():
            while self.running:
                time.sleep(30)  # Mostrar estadísticas cada 30 segundos
                if self.running:
                    self.show_stats()
        
        stats_thread_obj = threading.Thread(target=stats_thread)
        stats_thread_obj.daemon = True
        stats_thread_obj.start()
        
        try:
            # Esperar a que todos los threads terminen
            for thread in threads:
                thread.join()
                
        except KeyboardInterrupt:
            print("\nDeteniendo todos los bots...")
            self.running = False
            
            # Esperar que todos los threads terminen
            for thread in threads:
                thread.join(timeout=5)
        
        # Estadísticas finales
        self.show_final_stats()
    
    def show_final_stats(self):
        """Mostrar estadísticas finales"""
        with self.stats_lock:
            total_messages = sum(self.message_counts.values())
            total_errors = sum(self.error_counts.values())
            
            print("\n=== ESTADÍSTICAS FINALES ===")
            print(f"Total mensajes enviados: {total_messages}")
            print(f"Total errores: {total_errors}")
            if (total_messages + total_errors) > 0:
                print(f"Tasa de éxito: {(total_messages/(total_messages+total_errors)*100):.1f}%")
            
            print("\nPor bot:")
            for bot in self.bots:
                count = self.message_counts[bot["name"]]
                errors = self.error_counts[bot["name"]]
                print(f"  {bot['name']}: {count} mensajes, {errors} errores")

def main():
    """Función principal"""
    system = ConcurrentMultiBotSystem()
    system.start_all_bots()

if __name__ == "__main__":
    main()
