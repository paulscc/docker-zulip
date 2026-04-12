#!/usr/bin/env python3
"""
Multi-Bot Concurrent Optimizado - Gestión inteligente de carga para Gemma2
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

class OptimizedConcurrentMultiBotSystem:
    def __init__(self):
        """Inicializar sistema multi-bot concurrente optimizado"""
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
        
        # Cola para solicitudes a Gemma2 con límite para evitar sobrecarga
        self.gemma_queue = queue.Queue(maxsize=15)
        
        # Worker pool para Gemma2 (máximo 3 workers simultáneos)
        self.gemma_workers = []
        self.max_gemma_workers = 3
    
    def get_prompt_for_personality(self, personality):
        """Obtener prompt según la personalidad del bot"""
        prompts = {
            "friendly": [
                "Hola equipo",
                "Buen día a todos", 
                "¿Cómo están?",
                "Saludos equipo",
                "Qué tal",
                "Buen día",
                "Hola a todos",
                "Saludos"
            ],
            "casual": [
                "Qué onda equipo",
                "Buenas",
                "¿Qué hay de nuevo?",
                "Hey equipo",
                "Qué tal todo",
                "Buen día",
                "Qué hay",
                "Hola"
            ],
            "technical": [
                "Alguna novedad técnica",
                "Tips de código",
                "Tech update",
                "Novedades de desarrollo",
                "Consejo técnico",
                "Actualización",
                "Info técnica",
                "Dev news"
            ],
            "professional": [
                "Alguna sugerencia",
                "Buena práctica",
                "Mejora continua",
                "Productividad",
                "Objetivos",
                "Desarrollo profesional",
                "Eficiencia",
                "Progreso"
            ]
        }
        return random.choice(prompts.get(personality, prompts["friendly"]))
    
    def gemma_worker(self):
        """Worker dedicado para procesar solicitudes a Gemma2"""
        while self.running:
            try:
                # Obtener solicitud de la cola con timeout
                request = self.gemma_queue.get(timeout=1)
                
                bot_name, prompt, personality, callback, request_time = request
                
                # Esperar un poco si hay muchas solicitudes
                if self.gemma_queue.qsize() > 5:
                    time.sleep(random.uniform(0.5, 1.5))
                
                try:
                    personality_context = {
                        "friendly": "Eres amigable. ",
                        "casual": "Eres casual. ",
                        "technical": "Eres técnico. ",
                        "professional": "Eres profesional. "
                    }
                    
                    full_prompt = personality_context.get(personality, "") + prompt + " (responde muy corto, 1-2 palabras máximo)"
                    
                    payload = {
                        "model": self.model,
                        "prompt": full_prompt,
                        "stream": False
                    }
                    
                    response = requests.post(
                        f"{self.ollama_url}/api/generate",
                        json=payload,
                        timeout=8
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        message_content = result.get("response", "").strip()
                        callback(bot_name, message_content, None, request_time)
                    else:
                        callback(bot_name, None, f"Error Gemma2: {response.status_code}", request_time)
                
                except Exception as e:
                    callback(bot_name, None, f"Error: {str(e)[:50]}", request_time)
                
                finally:
                    self.gemma_queue.task_done()
                    # Pequeña pausa entre solicitudes
                    time.sleep(0.3)
                    
            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error en gemma_worker: {e}")
                time.sleep(1)
    
    def send_message_to_zulip(self, bot, content):
        """Enviar mensaje a Zulip usando form-data"""
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
            
        except Exception as e:
            return False, None
    
    def gemma_callback(self, bot_name, message_content, error, request_time):
        """Callback cuando Gemma2 responde"""
        try:
            bot = next((b for b in self.bots if b["name"] == bot_name), None)
            if not bot:
                return
            
            if error:
                with self.stats_lock:
                    self.error_counts[bot_name] += 1
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_name}: {error}")
            else:
                # Enviar mensaje a Zulip
                success, channel = self.send_message_to_zulip(bot, message_content)
                
                with self.stats_lock:
                    if success:
                        self.message_counts[bot_name] += 1
                        elapsed = time.time() - request_time
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_name}: Mensaje #{self.message_counts[bot_name]} a #{channel} ({elapsed:.1f}s)")
                    else:
                        self.error_counts[bot_name] += 1
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] {bot_name}: Error al enviar mensaje")
                        
        except Exception as e:
            with self.stats_lock:
                self.error_counts[bot_name] += 1
    
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
                
                # Generar prompt según personalidad
                prompt = self.get_prompt_for_personality(bot["personality"])
                
                # Agregar solicitud a la cola de Gemma2
                self.gemma_queue.put((bot["name"], prompt, bot["personality"], self.gemma_callback, start_time))
                
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
            print(f"Cola Gemma2: {self.gemma_queue.qsize()} solicitudes pendientes")
            
            for bot in self.bots:
                count = self.message_counts[bot["name"]]
                errors = self.error_counts[bot["name"]]
                print(f"  {bot['name']}: {count} mensajes, {errors} errores")
            
            print()
    
    def start_all_bots(self):
        """Iniciar todos los bots simultáneamente"""
        print("=== MULTI-BOT CONCURRENT OPTIMIZADO ===")
        print(f"Bots activos: {len(self.bots)}")
        print(f"Workers Gemma2: {self.max_gemma_workers} (máximo concurrente)")
        print("Cada bot opera independientemente con inicio aleatorio")
        print("Presiona Ctrl+C para detener todos los bots")
        print()
        
        # Probar conexiones
        connected_bots = self.test_all_connections()
        
        if not connected_bots:
            print("No se pudo conectar con ningún bot. Abortando.")
            return
        
        print(f"\nConectados {len(connected_bots)}/{len(self.bots)} bots")
        print("Iniciando workers de Gemma2...")
        
        # Iniciar workers de Gemma2
        for i in range(self.max_gemma_workers):
            worker = threading.Thread(target=self.gemma_worker)
            worker.daemon = True
            worker.start()
            self.gemma_workers.append(worker)
        
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
            
            for worker in self.gemma_workers:
                worker.join(timeout=5)
        
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
    system = OptimizedConcurrentMultiBotSystem()
    system.start_all_bots()

if __name__ == "__main__":
    main()
