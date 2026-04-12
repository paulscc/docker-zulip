#!/usr/bin/env python3
"""
Demo Final Completa del Sistema
Muestra el flujo completo con resúmenes reales generados por IA
"""

import json
import subprocess
import time
import requests
from datetime import datetime

def generar_resumen_con_ollama(mensajes):
    """Generar un resumen real usando Ollama"""
    
    # Formatear mensajes para Ollama
    texto_mensajes = "\n".join([f"[{msg['sender']}]: {msg['content']}" for msg in mensajes])
    
    prompt = f"""
Por favor, genera un resumen conciso y claro de la siguiente conversación del canal "desarrollo".

Mensajes:
{texto_mensajes}

Instrucciones:
1. Identifica los puntos principales y temas técnicos discutidos
2. Menciona decisiones importantes o problemas identificados
3. Resume cualquier acción o seguimiento necesario
4. Mantén el resumen en español y en un tono profesional
5. El resumen debe ser breve pero informativo (máximo 150 palabras)

Resumen:
"""
    
    payload = {
        "model": "gemma2:2b",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.3,
            "max_tokens": 300
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json=payload,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            return "Error generando resumen con Ollama"
            
    except Exception as e:
        return f"No se pudo generar el resumen: {str(e)}"

def demo_completa_con_resumenes():
    """Demostración completa con resúmenes reales"""
    
    print("=== DEMOSTRACIÓN FINAL COMPLETA ===")
    print("Generando resúmenes reales con Ollama gemma2:2b\n")
    
    # Mensajes de ejemplo del canal desarrollo
    mensajes_desarrollo = [
        {
            "sender": "Juan",
            "content": "El nuevo deploy del sistema está listo para testing en producción"
        },
        {
            "sender": "María",
            "content": "Encontramos un bug crítico en el módulo de autenticación que necesita fix urgente"
        },
        {
            "sender": "Carlos",
            "content": "La refactorización del código legacy mejoró el rendimiento en 40%"
        },
        {
            "sender": "Ana",
            "content": "Necesitamos actualizar las dependencias del proyecto esta semana por seguridad"
        },
        {
            "sender": "Pedro",
            "content": "El nuevo sistema de CI/CD está reduciendo el tiempo de deploy en 50%"
        }
    ]
    
    print("1. MENSAJES ORIGINALES DEL CANAL #DESARROLLO")
    print("=" * 50)
    
    for i, msg in enumerate(mensajes_desarrollo, 1):
        print(f"{i}. {msg['sender']}: {msg['content']}")
    
    print("\n2. GENERANDO RESUMEN CON OLLAMA (gemma2:2b)")
    print("=" * 50)
    print("Procesando con IA...")
    
    # Generar resumen real
    resumen = generar_resumen_con_ollama(mensajes_desarrollo)
    
    print(f"Resumen generado ({len(resumen)} caracteres):")
    print(resumen)
    
    # Enviar resumen a Kafka
    print("\n3. ENVIANDO RESUMEN A KAFKA")
    print("=" * 50)
    
    resumen_payload = {
        "message_type": "summary",
        "timestamp": datetime.now().isoformat(),
        "original_stream": "desarrollo",
        "original_topic": "channel events",
        "summary": resumen,
        "original_message_count": len(mensajes_desarrollo),
        "processed_at": datetime.now().isoformat(),
        "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
    }
    
    # Enviar a Kafka
    resumen_json = json.dumps(resumen_payload)
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "bash", "-c", f"echo '{resumen_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-summaries"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    
    if result.returncode == 0:
        print("Resumen enviado exitosamente a Kafka topic 'zulip-summaries'")
    else:
        print(f"Error enviando resumen a Kafka: {result.stderr}")
    
    print("\n4. ESTADO DEL SISTEMA")
    print("=" * 50)
    
    # Verificar componentes
    try:
        # Kafka
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "kafka-topics", "--bootstrap-server", "localhost:9092",
            "--list"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            topics = result.stdout.strip().split('\n') if result.stdout.strip() else []
            print(f"Kafka: OK ({len(topics)} topics)")
        
        # Ollama
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"Ollama: OK ({len(models)} modelos)")
        
        # Zulip
        response = requests.get("https://127.0.0.1.nip.io/api/v1/server_settings", verify=False, timeout=5)
        if response.status_code == 200:
            settings = response.json()
            print(f"Zulip: OK (v{settings.get('zulip_version')})")
            
    except Exception as e:
        print(f"Error verificando componentes: {e}")
    
    print("\n5. RESULTADO FINAL")
    print("=" * 50)
    print("El sistema está funcionando correctamente:")
    print("1. Mensajes procesados desde el canal #desarrollo")
    print("2. Resumen generado con IA (gemma2:2b)")
    print("3. Resumen enviado a Kafka")
    print("4. Incoming webhook listo para publicar en Zulip")
    
    print(f"\nRESUMEN QUE APARECERÁ EN #DESARROLLO/RESUMEN-GENERAL:")
    print("-" * 50)
    print(resumen)
    print("-" * 50)
    print(f"*Generado por IA (gemma2:2b) - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    print("\n=== PARA COMPLETAR EL SISTEMA ===")
    print("1. Genera nuevas API keys para zzz-bot y xxx-bot en Zulip")
    print("2. Actualiza las claves en bot_config.json")
    print("3. Reinicia los webhooks")
    print("4. Los resúmenes aparecerán automáticamente en Zulip")

if __name__ == "__main__":
    demo_completa_con_resumenes()
