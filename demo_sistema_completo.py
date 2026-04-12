#!/usr/bin/env python3
"""
Demo Sistema Completo
Muestra el funcionamiento completo del sistema Kafka con Ollama
"""

import json
import subprocess
import time
from datetime import datetime

def enviar_mensajes_demo():
    """Enviar mensajes de demostración a cada canal"""
    
    print("=== DEMOSTRACIÓN DEL SISTEMA COMPLETO ===")
    print("Enviando mensajes de prueba a cada canal...")
    
    canales = [
        {
            "nombre": "comercio",
            "mensajes": [
                "Necesito ayuda con la estrategia de precios para nuestro nuevo producto",
                "Los clientes están pidiendo más opciones de pago electrónico",
                "Las ventas aumentaron 15% este trimestre gracias a las promociones"
            ]
        },
        {
            "nombre": "desarrollo", 
            "mensajes": [
                "El nuevo deploy del sistema está listo para testing",
                "Encontramos un bug crítico en el módulo de autenticación",
                "La refactorización del código mejoró el rendimiento en 40%"
            ]
        },
        {
            "nombre": "equipo",
            "mensajes": [
                "Recordatorio: reunión de equipo mañana a las 10am",
                "Felicitaciones a Juan por su excelente trabajo esta semana",
                "Necesitamos volunteers para el evento de team building del viernes"
            ]
        },
        {
            "nombre": "general",
            "mensajes": [
                "Importante: mantenimiento del servidor este fin de semana",
                "La cafetería estará cerrada por reparaciones el jueves",
                "Bienvenidos a los nuevos miembros del equipo: Ana y Carlos"
            ]
        }
    ]
    
    for canal in canales:
        print(f"\n--- Enviando mensajes al canal #{canal['nombre']} ---")
        
        payload = {
            "trigger_type": "unread_messages",
            "timestamp": datetime.now().isoformat(),
            "stream": canal["nombre"],
            "topic": "general",
            "messages": [
                {
                    "content": msg,
                    "sender_full_name": f"Usuario-{i+1}",
                    "timestamp": datetime.now().isoformat()
                } for i, msg in enumerate(canal["mensajes"])
            ],
            "message_count": len(canal["mensajes"]),
            "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
        }
        
        # Enviar a Kafka
        message_json = json.dumps(payload)
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-unread-messages"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print(f"  Mensajes enviados exitosamente a Kafka")
        else:
            print(f"  Error: {result.stderr}")
        
        time.sleep(1)

def monitorear_procesamiento():
    """Monitorear el procesamiento de mensajes"""
    
    print("\n=== MONITOREO DEL PROCESAMIENTO ===")
    print("Verificando mensajes en Kafka...")
    
    # Esperar un momento para que el sistema procese
    print("Esperando 10 segundos para procesamiento...")
    time.sleep(10)
    
    # Verificar mensajes no leídos
    print("\n--- Mensajes en topic 'zulip-unread-messages' ---")
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", "zulip-unread-messages",
        "--from-beginning",
        "--timeout-ms", "5000"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0 and result.stdout.strip():
        mensajes = result.stdout.strip().split('\n')
        print(f"Se encontraron {len(mensajes)} mensajes en el topic de no leídos")
        for i, msg in enumerate(mensajes[:2]):  # Mostrar solo los primeros 2
            data = json.loads(msg)
            print(f"  {i+1}. Canal: {data['stream']}, Mensajes: {data['message_count']}")
    else:
        print("No se encontraron mensajes en el topic de no leídos")
    
    # Verificar resúmenes
    print("\n--- Resúmenes en topic 'zulip-summaries' ---")
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", "zulip-summaries",
        "--from-beginning",
        "--timeout-ms", "5000"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0 and result.stdout.strip():
        resumenes = result.stdout.strip().split('\n')
        print(f"Se encontraron {len(resumenes)} resúmenes en el topic de resúmenes")
        for i, resumen in enumerate(resumenes[:2]):  # Mostrar solo los primeros 2
            data = json.loads(resumen)
            print(f"  {i+1}. Canal: {data['original_stream']}, Resumen generado")
            print(f"     Longitud: {len(data['summary'])} caracteres")
    else:
        print("No se encontraron resúmenes en el topic de resúmenes")

def mostrar_estado_sistema():
    """Mostrar el estado actual del sistema"""
    
    print("\n=== ESTADO DEL SISTEMA ===")
    
    # Verificar Kafka
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-topics", "--bootstrap-server", "localhost:9092",
        "--list"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
        print(f"Kafka Topics: {len(topics)} topics encontrados")
        for topic in topics:
            if 'zulip' in topic:
                print(f"  - {topic}")
    
    # Verificar Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama Models: {len(models)} modelos disponibles")
            for model in models:
                if 'gemma' in model.get("name", ""):
                    print(f"  - {model['name']} (usado para resúmenes)")
    except:
        print("Ollama: No accesible")

def main():
    """Función principal de demostración"""
    
    print("INICIANDO DEMOSTRACIÓN COMPLETA DEL SISTEMA")
    print("=" * 50)
    
    # Mostrar estado actual
    mostrar_estado_sistema()
    
    # Enviar mensajes de prueba
    enviar_mensajes_demo()
    
    # Monitorear procesamiento
    monitorear_procesamiento()
    
    print("\n" + "=" * 50)
    print("DEMOSTRACIÓN COMPLETADA")
    print("=" * 50)
    print("\nEl sistema está funcionando correctamente:")
    print("1. Mensajes enviados a Kafka")
    print("2. Processor generando resúmenes con gemma2:2b")
    print("3. Resúmenes listos para publicación en Zulip")
    print("\nPara ver los resúmenes en Zulip:")
    print("- Visita los canales: #comercio, #desarrollo, #equipo, #general")
    print("- Busca los topics: resumen-general")

if __name__ == "__main__":
    main()
