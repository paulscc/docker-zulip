#!/usr/bin/env python3
"""
Send test messages to Kafka topics directly
"""

import requests
import json
from datetime import datetime

def send_test_to_kafka():
    """Send test messages to Kafka via webhook service"""
    
    url = "http://localhost:8080/kafka/send-unread"
    headers = {"Content-Type": "application/json"}
    
    payload = {
        "stream": "demo-kafka",
        "topic": "prueba-directa",
        "messages": [
            {
                "content": "Mensaje de prueba enviado directamente a Kafka topic 'zulip-unread-messages'",
                "sender_full_name": "Usuario Demo 1",
                "timestamp": datetime.now().isoformat()
            },
            {
                "content": "Este mensaje probará el flujo completo: Kafka → Ollama → Kafka summaries",
                "sender_full_name": "Usuario Demo 2", 
                "timestamp": datetime.now().isoformat()
            },
            {
                "content": "El sistema debería generar un resumen con estos 3 mensajes y publicarlo en 'zulip-summaries'",
                "sender_full_name": "Usuario Demo 3",
                "timestamp": datetime.now().isoformat()
            }
        ]
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            print("✅ Mensajes enviados exitosamente a Kafka!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error enviando mensajes: {e}")
        return False

if __name__ == "__main__":
    print("Enviando mensajes de prueba a Kafka...")
    send_test_to_kafka()
