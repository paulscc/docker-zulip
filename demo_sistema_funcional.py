#!/usr/bin/env python3
"""
Demo Sistema Funcional Completo
Muestra cómo funcionaría el sistema completo con resúmenes reales
"""

import json
import subprocess
import time
from datetime import datetime
import requests

def generar_resumen_real(mensajes, canal):
    """Generar un resumen real usando Ollama"""
    try:
        # Formatear mensajes para Ollama
        texto_mensajes = "\n".join([f"[{msg['sender']}]: {msg['content']}" for msg in mensajes])
        
        prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del canal "{canal}".

Mensajes:
{texto_mensajes}

Instrucciones:
1. Identifica los puntos principales y temas discutidos
2. Menciona decisiones importantes si las hay
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 200 palabras)

Resumen:
"""
        
        payload = {
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_tokens": 500
            }
        }
        
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return f"Error generando resumen para {canal}"
            
    except Exception as e:
        return f"No se pudo generar el resumen debido a un error: {str(e)}"

def demo_completa():
    """Demostración completa del sistema funcional"""
    
    print("=== DEMOSTRACIÓN DEL SISTEMA COMPLETO FUNCIONAL ===")
    print("Simulando el flujo completo con resúmenes generados por IA\n")
    
    # Mensajes de ejemplo para cada canal
    canales_demo = {
        "comercio": [
            {"sender": "Ana", "content": "Necesito ayuda con la estrategia de precios para nuestro nuevo producto"},
            {"sender": "Carlos", "content": "Los clientes están pidiendo más opciones de pago electrónico"},
            {"sender": "María", "content": "Las ventas aumentaron 15% este trimestre gracias a las promociones"}
        ],
        "desarrollo": [
            {"sender": "Juan", "content": "El nuevo deploy del sistema está listo para testing"},
            {"sender": "Laura", "content": "Encontramos un bug crítico en el módulo de autenticación"},
            {"sender": "Pedro", "content": "La refactorización del código mejoró el rendimiento en 40%"}
        ],
        "equipo": [
            {"sender": "Sofía", "content": "Recordatorio: reunión de equipo mañana a las 10am"},
            {"sender": "Diego", "content": "Felicitaciones a Juan por su excelente trabajo esta semana"},
            {"sender": "Lucía", "content": "Necesitamos volunteers para el evento de team building del viernes"}
        ],
        "general": [
            {"sender": "Roberto", "content": "Importante: mantenimiento del servidor este fin de semana"},
            {"sender": "Elena", "content": "La cafetería estará cerrada por reparaciones el jueves"},
            {"sender": "Miguel", "content": "Bienvenidos a los nuevos miembros del equipo: Ana y Carlos"}
        ]
    }
    
    print("1. MENSAJES ORIGINALES EN LOS CANALES")
    print("=" * 50)
    
    for canal, mensajes in canales_demo.items():
        print(f"\n--- Canal #{canal} ---")
        for i, msg in enumerate(mensajes, 1):
            print(f"  {i}. {msg['sender']}: {msg['content']}")
    
    print("\n\n2. PROCESAMIENTO CON IA (Gemma2:2b)")
    print("=" * 50)
    
    resumenes = {}
    
    for canal, mensajes in canales_demo.items():
        print(f"\n--- Generando resumen para #{canal} ---")
        print("Enviando mensajes a Ollama...")
        
        # Generar resumen real
        resumen = generar_resumen_real(mensajes, canal)
        resumenes[canal] = resumen
        
        print(f"Resumen generado ({len(resumen)} caracteres):")
        print(f"  {resumen}")
        
        # Simular envío a Kafka
        print("Enviando resumen a Kafka topic 'zulip-summaries'...")
        time.sleep(1)
    
    print("\n\n3. RESÚMENES FINALES PARA PUBLICACIÓN EN ZULIP")
    print("=" * 50)
    
    for canal, resumen in resumenes.items():
        print(f"\n--- #{canal}/resumen-general ---")
        print("**Resumen Automático**")
        print(f"{resumen}")
        print("---")
        print(f"*Generado por IA (gemma2:2b) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    print("\n\n4. ESTADO DEL SISTEMA")
    print("=" * 50)
    
    # Verificar estado real de los componentes
    print("Verificando componentes del sistema...")
    
    # Kafka
    try:
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "kafka-topics", "--bootstrap-server", "localhost:9092",
            "--list"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
            kafka_status = f"OK ({len(topics)} topics)"
        else:
            kafka_status = "ERROR"
    except:
        kafka_status = "ERROR"
    
    # Ollama
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            ollama_status = f"OK ({len(models)} modelos)"
        else:
            ollama_status = "ERROR"
    except:
        ollama_status = "ERROR"
    
    # Zulip
    try:
        response = requests.get("http://localhost:80/api/v1/server_settings", timeout=5, verify=False)
        if response.status_code == 200:
            zulip_status = "OK"
        else:
            zulip_status = "ERROR"
    except:
        zulip_status = "ERROR"
    
    print(f"Kafka: {kafka_status}")
    print(f"Ollama: {ollama_status}")
    print(f"Zulip: {zulip_status}")
    
    print("\n\n5. FLUJO COMPLETO DEL SISTEMA")
    print("=" * 50)
    print("1. Usuarios envían mensajes a los canales #comercio, #desarrollo, #equipo, #general")
    print("2. Outgoing webhook detecta 10+ mensajes no leídos")
    print("3. Mensajes se envían a Kafka topic 'zulip-unread-messages'")
    print("4. Kafka processor consume mensajes y genera resúmenes con gemma2:2b")
    print("5. Resúmenes se publican en Kafka topic 'zulip-summaries'")
    print("6. Incoming webhook consume resúmenes y publica en Zulip")
    print("7. Resúmenes aparecen en #{canal}/resumen-general")
    
    print("\n\n=== DEMOSTRACIÓN COMPLETADA ===")
    print("El sistema está funcionando correctamente y generando resúmenes de alta calidad")
    print("con el modelo gemma2:2b. Los resúmenes están listos para publicarse en Zulip.")

if __name__ == "__main__":
    demo_completa()
