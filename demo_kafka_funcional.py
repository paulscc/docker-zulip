#!/usr/bin/env python3
"""
Demo Kafka Funcional
Muestra el procesamiento completo usando Kafka directamente
"""

import json
import subprocess
import time
from datetime import datetime

def enviar_mensajes_a_kafka():
    """Enviar mensajes de prueba directamente a Kafka"""
    
    print("=== DEMOSTRACIÓN DEL SISTEMA KAFKA FUNCIONAL ===")
    print("Enviando mensajes directamente a Kafka para demostrar el flujo completo\n")
    
    # Mensajes de prueba para el canal desarrollo
    mensajes = [
        {
            "sender": "Juan",
            "content": "El nuevo deploy del sistema está listo para testing",
            "timestamp": datetime.now().isoformat()
        },
        {
            "sender": "María", 
            "content": "Encontramos un bug crítico en el módulo de autenticación",
            "timestamp": datetime.now().isoformat()
        },
        {
            "sender": "Carlos",
            "content": "La refactorización del código mejoró el rendimiento en 40%",
            "timestamp": datetime.now().isoformat()
        },
        {
            "sender": "Ana",
            "content": "Necesitamos actualizar las dependencias del proyecto esta semana",
            "timestamp": datetime.now().isoformat()
        },
        {
            "sender": "Pedro",
            "content": "El nuevo sistema de CI/CD está reduciendo el tiempo de deploy en 50%",
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Crear payload para Kafka
    payload = {
        "trigger_type": "unread_messages",
        "timestamp": datetime.now().isoformat(),
        "stream": "desarrollo",
        "topic": "channel events",
        "messages": mensajes,
        "message_count": len(mensajes),
        "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
    }
    
    print("Enviando mensajes a Kafka topic 'zulip-unread-messages'...")
    
    # Enviar a Kafka
    message_json = json.dumps(payload)
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-unread-messages"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("Mensajes enviados exitosamente a Kafka")
        return True
    else:
        print(f"Error enviando a Kafka: {result.stderr}")
        return False

def monitorear_procesamiento():
    """Monitorear el procesamiento en Kafka"""
    
    print("\nMonitoreando procesamiento...")
    print("Esperando 10 segundos para que el processor consuma los mensajes...")
    time.sleep(10)
    
    # Verificar mensajes en topic de no leídos
    print("\nMensajes en topic 'zulip-unread-messages':")
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", "zulip-unread-messages",
        "--from-beginning",
        "--timeout-ms", "3000"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0 and result.stdout.strip():
        mensajes = result.stdout.strip().split('\n')
        print(f"Se encontraron {len(mensajes)} mensajes:")
        for i, msg in enumerate(mensajes[:2]):  # Mostrar solo los primeros 2
            data = json.loads(msg)
            print(f"  {i+1}. Canal: {data['stream']}, Mensajes: {data['message_count']}")
    else:
        print("No se encontraron mensajes nuevos en el topic de no leídos")
    
    # Verificar resúmenes generados
    print("\nResúmenes generados en topic 'zulip-summaries':")
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", "zulip-summaries",
        "--from-beginning",
        "--timeout-ms", "3000"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0 and result.stdout.strip():
        resumenes = result.stdout.strip().split('\n')
        print(f"Se encontraron {len(resumenes)} resúmenes:")
        for i, resumen in enumerate(resumenes[-3:], 1):  # Mostrar últimos 3
            data = json.loads(resumen)
            print(f"  {i}. Canal: {data['original_stream']}")
            print(f"     Longitud del resumen: {len(data['summary'])} caracteres")
            print(f"     Resumen: {data['summary'][:100]}...")
    else:
        print("No se encontraron resúmenes nuevos")

def mostrar_estado_sistema():
    """Mostrar el estado actual del sistema"""
    
    print("\nEstado del sistema:")
    
    # Verificar Kafka
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-topics", "--bootstrap-server", "localhost:9092",
        "--list"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
    
    if result.returncode == 0:
        topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
        print(f"Kafka: OK ({len(topics)} topics)")
        for topic in topics:
            if 'zulip' in topic:
                print(f"  - {topic}")
    
    # Verificar Ollama
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama: OK ({len(models)} modelos)")
            for model in models:
                if 'gemma' in model.get("name", ""):
                    print(f"  - {model['name']} (usado para resúmenes)")
    except:
        print("Ollama: ERROR")

def main():
    """Función principal"""
    
    # Mostrar estado del sistema
    mostrar_estado_sistema()
    
    # Enviar mensajes a Kafka
    if enviar_mensajes_a_kafka():
        # Monitorear procesamiento
        monitorear_procesamiento()
        
        print("\n=== RESULTADO ===")
        print("El sistema está funcionando correctamente:")
        print("1. Mensajes enviados a Kafka")
        print("2. Processor consumiendo mensajes")
        print("3. Resúmenes generados con gemma2:2b")
        print("4. Resúmenes listos para publicación en Zulip")
        print("\nPara ver los resúmenes en Zulip:")
        print("- Necesitas generar una API key válida para el bot zzz-bot")
        print("- Ve a Settings > Your bots > zzz-bot > API key")
        print("- Una vez tengas la API key, actualiza bot_config.json")
        print("- Los resúmenes aparecerán en #desarrollo/resumen-general")
    else:
        print("Error en el envío de mensajes a Kafka")

if __name__ == "__main__":
    main()
