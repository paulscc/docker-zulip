#!/usr/bin/env python3
"""
Enviar Mensajes al Canal #desarrollo
Enviar mensajes de prueba al canal donde está el usuario
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enviar_mensajes_desarrollo():
    """Enviar mensajes de prueba al canal #desarrollo"""
    
    # Usar la URL donde está el usuario
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "https://127.0.0.1.nip.io"
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")  # HTTP Basic Auth
    
    mensajes = [
        "¡Hola equipo! Este es un mensaje de prueba para el sistema de webhooks automáticos",
        "El sistema de Kafka está funcionando correctamente y procesando mensajes",
        "Ollama con modelo gemma2:2b está generando resúmenes de alta calidad",
        "Los resúmenes deberían aparecer automáticamente en este canal",
        "Este es el último mensaje de prueba - deberíamos ver un resumen pronto"
    ]
    
    print(f"Enviando {len(mensajes)} mensajes al canal #desarrollo...")
    print(f"Servidor: {server_url}")
    
    for i, mensaje in enumerate(mensajes, 1):
        payload = {
            "type": "stream",
            "to": "desarrollo",
            "topic": "channel events",  # Mismo topic donde está el usuario
            "content": f"{mensaje}\n\n*Mensaje de prueba #{i} - {datetime.now().strftime('%H:%M:%S')}*"
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
                print(f"  Mensaje {i} enviado exitosamente")
            else:
                print(f"  Error mensaje {i}: {response.status_code}")
                if response.status_code == 401:
                    print("    Error de autenticación - la API key puede no ser válida")
                elif response.status_code == 400:
                    print("    Error en el formato de la solicitud")
                print(f"    Response: {response.text}")
            
            time.sleep(1)  # Pequeña pausa entre mensajes
            
        except Exception as e:
            print(f"  Error mensaje {i}: {e}")
    
    return True

def verificar_estado_componentes():
    """Verificar el estado de los componentes del sistema"""
    
    print("\nVerificando estado de los componentes...")
    
    # Verificar Kafka
    try:
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "kafka-topics", "--bootstrap-server", "localhost:9092",
            "--list"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"Kafka: OK ({len(topics)} topics)")
        else:
            print("Kafka: ERROR")
    except:
        print("Kafka: ERROR")
    
    # Verificar Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama: OK ({len(models)} modelos)")
        else:
            print("Ollama: ERROR")
    except:
        print("Ollama: ERROR")
    
    # Verificar Zulip
    try:
        response = requests.get(f"{server_url}/api/v1/server_settings", verify=False, timeout=5)
        if response.status_code == 200:
            settings = response.json()
            print(f"Zulip: OK (v{settings.get('zulip_version')})")
        else:
            print("Zulip: ERROR")
    except:
        print("Zulip: ERROR")

def main():
    """Función principal"""
    
    print("=== ENVIANDO MENSAJES AL CANAL #DESARROLLO ===")
    print("Enviando mensajes de prueba al canal donde estás ubicado\n")
    
    # Verificar componentes
    verificar_estado_componentes()
    
    print("\nEnviando mensajes...")
    enviar_mensajes_desarrollo()
    
    print("\n=== INSTRUCCIONES ===")
    print("1. Deberías ver los mensajes appearing en el canal #desarrollo")
    print("2. El sistema debería detectar los mensajes no leídos")
    print("3. Los mensajes se enviarán a Kafka para procesamiento")
    print("4. Se generarán resúmenes con gemma2:2b")
    print("5. Los resúmenes aparecerán en #desarrollo/resumen-general")
    print("\nEspera unos minutos para ver el procesamiento completo.")

if __name__ == "__main__":
    import subprocess
    main()
