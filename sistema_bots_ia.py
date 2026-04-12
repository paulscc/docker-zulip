#!/usr/bin/env python3
"""
Sistema de Bots con IA
Todos los bots genéricos envían mensajes aleatorios generados por gemma2
El outgoing webhook toma estos mensajes y genera resúmenes
"""

import json
import subprocess
import time
import random
import threading
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class SistemaBotsIA:
    def __init__(self):
        """Inicializar el sistema de bots con IA"""
        self.server_url = "https://127.0.0.1.nip.io"
        self.ollama_url = "http://localhost:11434"
        
        # Todos los bots genéricos disponibles
        self.bots_genericos = [
            {"email": "aaa-bot@127.0.0.1.nip.io", "key": "f68mFE6Ihur5eNW58V2b3jE7cPvqOsWw", "name": "aaa-bot"},
            {"email": "bbb-bot@127.0.0.1.nip.io", "key": "39EB0ERDtAEPi63lMP77aEQ9NrUI2fp4", "name": "bbb-bot"},
            {"email": "ddd-bot@127.0.0.1.nip.io", "key": "WqEhRLLFVBktfSjGdquLIJ84b52q3VB8", "name": "ddd-bot"},
            {"email": "eee-bot@127.0.0.1.nip.io", "key": "KKONeQT2YEC6q2fwENt0vSqwzrkDUmbT", "name": "eee-bot"},
            {"email": "fff-bot@127.0.0.1.nip.io", "key": "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv", "name": "fff-bot"},
            {"email": "ggg-bot@127.0.0.1.nip.io", "key": "l71o3mHodGNViO3DEpQFYUKTKHA1PQsk", "name": "ggg-bot"},
            {"email": "hhh-bot@127.0.0.1.nip.io", "key": "lgCtjcfOlY4s2vVXRuBKDRszr4YlyJ8t", "name": "hhh-bot"},
            {"email": "iii-bot@127.0.0.1.nip.io", "key": "oNhze1f1pF7mWWfLsLllSU6qCX3pgnJ6", "name": "iii-bot"},
            {"email": "jjj-bot@127.0.0.1.nip.io", "key": "xCr4tCZdbBUhPSjX594fOkt6U4a6qaRT", "name": "jjj-bot"},
            {"email": "kkk-bot@127.0.0.1.nip.io", "key": "j23GPTvEPcbUw5dtqqy2gKAkEI8c3lvJ", "name": "kkk-bot"}
        ]
        
        # Canales y temas para los bots
        self.canales_temas = {
            "comercio": [
                "estrategias de precios y ventas",
                "nuevos productos y servicios",
                "feedback de clientes y satisfacción",
                "marketing y campañas publicitarias",
                "logística y distribución",
                "análisis de mercado y competencia"
            ],
            "desarrollo": [
                "desarrollo de software y nuevas features",
                "bugs y fixes del sistema",
                "deploy y producción",
                "mejoras de rendimiento y optimización",
                "seguridad y vulnerabilidades",
                "arquitectura y refactorización"
            ],
            "equipo": [
                "reuniones y coordinación del equipo",
                "eventos y team building",
                "evaluaciones de desempeño",
                "nuevos miembros y bienvenida",
                "políticas y procedimientos internos",
                "celebraciones y reconocimientos"
            ],
            "general": [
                "mantenimiento y operaciones",
                "anuncios importantes de la empresa",
                "políticas y reglamentos",
                "servicios y facilidades",
                "seguridad y emergencias",
                "eventos generales de la compañía"
            ]
        }
        
        self.threads_activos = []
        self.detener = False
        self.mensajes_enviados = 0
    
    def generar_mensaje_con_ia(self, canal, tema):
        """Generar un mensaje aleatorio usando gemma2"""
        
        prompt = f"""
Genera un mensaje breve y natural para un chat de trabajo sobre el tema: "{tema}" en el canal "{canal}".

Instrucciones:
1. El mensaje debe sonar como si lo escribiera un empleado real
2. Debe ser breve (1-2 frases máximo)
3. Debe ser relevante para el tema y canal
4. No uses saludos ni firmas
5. Sé conversacional y natural

Mensaje:"""
        
        payload = {
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.8,
                "max_tokens": 100
            }
        }
        
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                result = response.json()
                mensaje = result.get("response", "").strip()
                # Limpiar el mensaje
                mensaje = mensaje.replace('"', '').replace('\n', ' ').strip()
                if len(mensaje) > 150:
                    mensaje = mensaje[:150] + "..."
                return mensaje
            else:
                return f"Mensaje sobre {tema} en el canal {canal}"
                
        except Exception as e:
            return f"Trabajando en {tema} para el canal {canal}"
    
    def enviar_mensaje_a_kafka(self, canal, bot, mensaje):
        """Enviar mensaje directamente a Kafka (simulando que viene de Zulip)"""
        
        # Crear mensaje en formato Zulip
        mensaje_zulip = {
            "sender_full_name": bot["name"],
            "content": mensaje,
            "timestamp": datetime.now().isoformat(),
            "stream": canal,
            "topic": "general"
        }
        
        # Enviar a Kafka como si fuera un mensaje de Zulip
        payload = {
            "trigger_type": "unread_messages",
            "timestamp": datetime.now().isoformat(),
            "stream": canal,
            "topic": "general",
            "messages": [mensaje_zulup],
            "message_count": 1,
            "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
        }
        
        # Enviar a Kafka
        message_json = json.dumps(payload)
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-unread-messages"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] {canal}: {bot['name']} - {mensaje[:60]}...")
                self.mensajes_enviados += 1
                return True
            else:
                print(f"Error enviando mensaje a Kafka: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False
    
    def bot_activo(self, bot):
        """Hilo que simula un bot activo generando mensajes con IA"""
        
        # Inicio aleatorio (0-30 segundos)
        inicio_aleatorio = random.uniform(0, 30)
        time.sleep(inicio_aleatorio)
        
        mensajes_bot = 0
        
        while not self.detener:
            # Seleccionar canal aleatorio
            canal = random.choice(list(self.canales_temas.keys()))
            
            # Seleccionar tema aleatorio para ese canal
            tema = random.choice(self.canales_temas[canal])
            
            # Generar mensaje con IA
            mensaje = self.generar_mensaje_con_ia(canal, tema)
            
            # Enviar a Kafka
            self.enviar_mensaje_a_kafka(canal, bot, mensaje)
            mensajes_bot += 1
            
            # Esperar entre 5-15 segundos para el siguiente mensaje
            espera = random.uniform(5, 15)
            time.sleep(espera)
        
        print(f"{bot['name']}: Enviados {mensajes_bot} mensajes")
    
    def iniciar_sistema(self):
        """Iniciar el sistema completo de bots con IA"""
        
        print("=== SISTEMA DE BOTS CON IA ===")
        print("Todos los bots genéricos enviarán mensajes generados por gemma2")
        print("El outgoing webhook tomará estos mensajes y generará resúmenes\n")
        
        print(f"Bots activos: {len(self.bots_genericos)}")
        print("Canales monitoreados: comercio, desarrollo, equipo, general")
        print("Modelo de IA: gemma2:2b")
        print("Intervalo de mensajes: 5-15 segundos por bot\n")
        
        # Crear hilos para cada bot
        for bot in self.bots_genericos:
            thread = threading.Thread(
                target=self.bot_activo,
                args=(bot,)
            )
            thread.daemon = True
            self.threads_activos.append(thread)
            thread.start()
        
        # Mostrar estadísticas
        self.mostrar_estadisticas()
        
        # Esperar a que todos terminen
        try:
            while any(thread.is_alive() for thread in self.threads_activos):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo sistema de bots...")
            self.detener = True
        
        print(f"\nSistema detenido. Total de mensajes enviados: {self.mensajes_enviados}")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas en tiempo real"""
        
        while not self.detener:
            try:
                # Verificar mensajes en Kafka
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", "zulip-unread-messages",
                    "--from-beginning",
                    "--timeout-ms", "2000"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    mensajes = result.stdout.strip().split('\n')
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] Total mensajes en Kafka: {len(mensajes)} | Enviados por bots: {self.mensajes_enviados}")
                
                # Verificar resúmenes generados
                cmd_resumenes = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", "zulip-summaries",
                    "--from-beginning",
                    "--timeout-ms", "2000"
                ]
                
                result_resumenes = subprocess.run(cmd_resumenes, capture_output=True, text=True, timeout=10)
                
                if result_resumenes.returncode == 0 and result_resumenes.stdout.strip():
                    resumenes = result_resumenes.stdout.strip().split('\n')
                    print(f"[{timestamp}] Resúmenes generados: {len(resumenes)}")
                
                time.sleep(30)  # Mostrar estadísticas cada 30 segundos
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error en estadísticas: {e}")
                time.sleep(30)

def main():
    """Función principal"""
    
    sistema = SistemaBotsIA()
    
    try:
        sistema.iniciar_sistema()
    except KeyboardInterrupt:
        print("\nSistema detenido por usuario")

if __name__ == "__main__":
    main()
