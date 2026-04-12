#!/usr/bin/env python3
"""
Publicador de Resúmenes
Usa un bot regular para publicar resúmenes en Zulip
"""

import requests
import json
import time
from datetime import datetime
import urllib3
import subprocess

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class PublicadorResumenes:
    def __init__(self):
        """Inicializar el publicador de resúmenes"""
        # Usar uno de los bots regulares que sí puede enviar mensajes
        self.api_key = "f68mFE6Ihur5eNW58V2b3jE7cPvqOsWw"  # aaa-bot
        self.email = "aaa-bot@127.0.0.1.nip.io"
        self.server_url = "https://127.0.0.1.nip.io"
        
    def probar_conexion(self):
        """Probar conexión con el bot regular"""
        
        headers = {
            "Content-Type": "application/json"
        }
        auth = (self.email, self.api_key)
        
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
                print(f"Conexión exitosa: {user_data.get('full_name', 'Unknown')}")
                return True
            else:
                print(f"Error de conexión: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def publicar_resumen(self, canal, topic, resumen):
        """Publicar un resumen en un canal de Zulip"""
        
        headers = {
            "Content-Type": "application/json"
        }
        auth = (self.email, self.api_key)
        
        payload = {
            "type": "stream",
            "to": canal,
            "topic": topic,
            "content": f"""**Resumen Automático del Canal #{canal}**

{resumen}

---
*Generado por IA (gemma2:2b) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
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
                print(f"Resumen publicado exitosamente en #{canal}/{topic}")
                return True
            else:
                print(f"Error publicando resumen: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"Error publicando resumen: {e}")
            return False
    
    def consumir_resumenes_de_kafka(self):
        """Consumir resúmenes de Kafka y publicarlos en Zulip"""
        
        print("Iniciando consumidor de resúmenes de Kafka...")
        
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
                        
                        if resumen and "Error" not in resumen:
                            # Publicar en Zulip
                            topic = f"resumen-{canal}"
                            success = self.publicar_resumen(canal, topic, resumen)
                            
                            if success:
                                print(f"Resumen publicado para {canal}")
                            else:
                                print(f"Error publicando resumen para {canal}")
                        else:
                            print("Resumen con error o vacío, omitiendo")
                            
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
                print("Deteniendo publicador de resúmenes...")
                break
            except Exception as e:
                print(f"Error en el ciclo: {e}")
                time.sleep(10)

def main():
    """Función principal"""
    
    print("=== PUBLICADOR DE RESÚMENES PARA ZULIP ===")
    print("Usando bot regular para publicar resúmenes generados por Kafka\n")
    
    publicador = PublicadorResumenes()
    
    # Probar conexión
    if not publicador.probar_conexion():
        print("No se puede conectar a Zulip. Abortando.")
        return
    
    # Iniciar consumidor de resúmenes
    print("Iniciando consumo y publicación de resúmenes...")
    print("Los resúmenes aparecerán en los canales como #{canal}/resumen-{canal}")
    print("Presiona Ctrl+C para detener\n")
    
    try:
        publicador.consumir_resumenes_de_kafka()
    except KeyboardInterrupt:
        print("\nPublicador detenido por usuario")

if __name__ == "__main__":
    main()
