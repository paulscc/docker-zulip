#!/usr/bin/env python3
"""
Publicador Multi-Bot
Usa múltiples bots genéricos para publicar resúmenes en Zulip
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import subprocess

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PublicadorMultiBot:
    def __init__(self):
        """Inicializar el publicador multi-bot"""
        self.server_url = "https://127.0.0.1.nip.io"
        
        # Lista de bots genéricos disponibles
        self.bots = [
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
        
        self.bot_actual = None
        self.bot_index = 0
        
    def probar_bot(self, bot):
        """Probar si un bot puede conectar a Zulip"""
        
        headers = {
            "Content-Type": "application/json"
        }
        auth = (bot["email"], bot["key"])
        
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/users/me",
                headers=headers,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                print(f"  {bot['name']}: OK - {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                print(f"  {bot['name']}: ERROR {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  {bot['name']}: ERROR - {e}")
            return False
    
    def encontrar_bot_funcional(self):
        """Encontrar el primer bot que funcione"""
        
        print("Buscando bot funcional...")
        
        for i, bot in enumerate(self.bots):
            if self.probar_bot(bot):
                self.bot_actual = bot
                self.bot_index = i
                print(f"Bot seleccionado: {bot['name']}")
                return True
        
        print("No se encontró ningún bot funcional")
        return False
    
    def cambiar_bot_siguiente(self):
        """Cambiar al siguiente bot disponible"""
        
        print(f"Cambiando del bot {self.bot_actual['name']} al siguiente...")
        
        # Probar bots restantes
        for i in range(len(self.bots)):
            next_index = (self.bot_index + 1 + i) % len(self.bots)
            next_bot = self.bots[next_index]
            
            if self.probar_bot(next_bot):
                self.bot_actual = next_bot
                self.bot_index = next_index
                print(f"Nuevo bot seleccionado: {next_bot['name']}")
                return True
        
        print("No hay más bots funcionales disponibles")
        return False
    
    def publicar_resumen(self, canal, topic, resumen, reintentos=3):
        """Publicar un resumen con sistema de reintentos y fallback"""
        
        for intento in range(reintentos):
            if not self.bot_actual:
                if not self.encontrar_bot_funcional():
                    return False
            
            headers = {
                "Content-Type": "application/json"
            }
            auth = (self.bot_actual["email"], self.bot_actual["key"])
            
            payload = {
                "type": "stream",
                "to": canal,
                "topic": topic,
                "content": f"""**Resumen Automático del Canal #{canal}**

{resumen}

---
*Generado por IA (gemma2:2b) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Publicado por: {self.bot_actual['name']}*
*Basado en mensajes procesados por Kafka*"""
            }
            
            try:
                response = requests.post(
                    f"{self.server_url}/api/v1/messages",
                    headers=headers,
                    json=payload,
                    auth=auth,
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print(f"Resumen publicado exitosamente por {self.bot_actual['name']} en #{canal}/{topic}")
                    return True
                else:
                    print(f"Error publicando con {self.bot_actual['name']}: {response.status_code}")
                    
                    # Si falla, intentar con otro bot
                    if intento < reintentos - 1:
                        print("Intentando con otro bot...")
                        if not self.cambiar_bot_siguiente():
                            return False
                    
            except Exception as e:
                print(f"Error publicando resumen: {e}")
                
                # Si hay error, intentar con otro bot
                if intento < reintentos - 1:
                    print("Intentando con otro bot...")
                    if not self.cambiar_bot_siguiente():
                        return False
        
        return False
    
    def consumir_resumenes_de_kafka(self):
        """Consumir resúmenes de Kafka y publicarlos en Zulip"""
        
        print("Iniciando publicador multi-bot de resúmenes de Kafka...")
        
        # Encontrar bot funcional inicial
        if not self.encontrar_bot_funcional():
            print("No se puede encontrar un bot funcional. Abortando.")
            return
        
        print(f"Usando bot inicial: {self.bot_actual['name']}")
        print("Los resúmenes aparecerán en los canales como #{canal}/resumen-{canal}")
        print("Presiona Ctrl+C para detener\n")
        
        resumen_count = 0
        
        while True:
            try:
                # Consumir resúmenes de Kafka
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", "zulip-summaries",
                    "--from-beginning",
                    "--max-messages", "1",
                    "--timeout-ms", "5000"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    # Parsear el JSON del resumen
                    try:
                        resumen_data = json.loads(result.stdout.strip())
                        
                        # Extraer datos del resumen
                        canal = resumen_data.get("original_stream", "general")
                        resumen = resumen_data.get("summary", "")
                        
                        if resumen and "Error" not in resumen and len(resumen) > 50:
                            # Publicar en Zulip
                            topic = f"resumen-{canal}"
                            success = self.publicar_resumen(canal, topic, resumen)
                            
                            if success:
                                resumen_count += 1
                                print(f"Total de resúmenes publicados: {resumen_count}")
                            else:
                                print("Error publicando resumen, reintentando...")
                        else:
                            print("Resumen con error o demasiado corto, omitiendo")
                            
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
                    except Exception as e:
                        print(f"Error procesando resumen: {e}")
                else:
                    # No hay resúmenes nuevos, esperar
                    time.sleep(5)
                
            except subprocess.TimeoutExpired:
                # Timeout normal cuando no hay mensajes
                time.sleep(5)
            except KeyboardInterrupt:
                print(f"\nPublicador detenido por usuario")
                print(f"Total de resúmenes publicados: {resumen_count}")
                break
            except Exception as e:
                print(f"Error en el ciclo: {e}")
                time.sleep(10)

def main():
    """Función principal"""
    
    print("=== PUBLICADOR MULTI-BOT PARA ZULIP ===")
    print("Usando múltiples bots genéricos para publicar resúmenes\n")
    
    publicador = PublicadorMultiBot()
    
    # Iniciar consumidor de resúmenes
    try:
        publicador.consumir_resumenes_de_kafka()
    except KeyboardInterrupt:
        print("\nPublicador detenido por usuario")

if __name__ == "__main__":
    main()
