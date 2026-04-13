#!/usr/bin/env python3
"""
Test script to verify messages include links in Kafka topics
"""

import requests
import json
import subprocess
from datetime import datetime

def test_kafka_messages_with_links():
    """Test that messages in Kafka include direct links"""
    
    print("Verificando mensajes con enlaces en Kafka topics...")
    print("="*60)
    
    # Check unread messages topic
    print("\n1. Verificando topic 'zulip-unread-messages':")
    print("-" * 40)
    
    cmd_unread = [
        "docker", "exec", "opcion2-kafka-1",
        "kafka-console-consumer",
        "--bootstrap-server", "localhost:9092",
        "--topic", "zulip-unread-messages",
        "--from-beginning",
        "--timeout-ms", "5000"
    ]
    
    result_unread = subprocess.run(cmd_unread, capture_output=True, text=True, timeout=10)
    
    if result_unread.returncode == 0 and result_unread.stdout.strip():
        messages = result_unread.stdout.strip().split('\n')
        
        # Find the most recent message with links
        for msg in reversed(messages[-3:]):  # Check last 3 messages
            try:
                data = json.loads(msg)
                message_list = data.get("messages", [])
                
                if message_list:
                    sample_msg = message_list[0]
                    print(f"Stream: {data.get('stream')}")
                    print(f"Topic: {data.get('topic')}")
                    print(f"Message count: {data.get('message_count')}")
                    print(f"Sample message:")
                    print(f"  - Content: {sample_msg.get('content', '')[:50]}...")
                    print(f"  - Sender: {sample_msg.get('sender_full_name', 'N/A')}")
                    print(f"  - Direct Link: {sample_msg.get('direct_link', 'NO LINK')}")
                    print(f"  - Message ID: {sample_msg.get('id', 'N/A')}")
                    
                    if sample_msg.get('direct_link'):
                        print("  **ENLACE DIRECTO INCLUIDO CORRECTAMENTE**")
                    else:
                        print("  **ERROR: No se encontró enlace directo**")
                    
                    print()
                    break
                    
            except json.JSONDecodeError:
                continue
    else:
        print("No se encontraron mensajes en 'zulip-unread-messages'")
    
    # Send a test message with the updated webhook
    print("\n2. Enviando mensaje de prueba con enlaces:")
    print("-" * 40)
    
    # Use the webhook service to send a test message
    test_payload = {
        "stream": "test-links",
        "topic": "prueba-enlaces",
        "messages": [
            {
                "id": 12345,
                "content": "Este es un mensaje de prueba para verificar que los enlaces se incluyen correctamente en Kafka",
                "sender_full_name": "Usuario Test Enlaces",
                "timestamp": datetime.now().isoformat(),
                "direct_link": "https://localhost:443/#narrow/stream/123/topic/456/near/12345",
                "reactions": [],
                "flags": {}
            }
        ]
    }
    
    try:
        response = requests.post(
            "http://localhost:8080/kafka/send-unread",
            json=test_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            print("Mensaje de prueba enviado exitosamente a Kafka")
            print(f"Response: {response.json()}")
        else:
            print(f"Error enviando mensaje: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Check the test message in Kafka
    print("\n3. Verificando mensaje de prueba en Kafka:")
    print("-" * 40)
    
    import time
    time.sleep(2)  # Wait for message to be processed
    
    result_test = subprocess.run(cmd_unread, capture_output=True, text=True, timeout=10)
    
    if result_test.returncode == 0 and result_test.stdout.strip():
        test_messages = result_test.stdout.strip().split('\n')
        
        for msg in reversed(test_messages[-2:]):  # Check last 2 messages
            try:
                data = json.loads(msg)
                if data.get('stream') == 'test-links' and data.get('topic') == 'prueba-enlaces':
                    message_list = data.get("messages", [])
                    if message_list:
                        sample_msg = message_list[0]
                        print("Mensaje de prueba encontrado:")
                        print(f"  - Content: {sample_msg.get('content', '')}")
                        print(f"  - Direct Link: {sample_msg.get('direct_link', 'NO LINK')}")
                        print(f"  - Message ID: {sample_msg.get('id', 'N/A')}")
                        
                        if sample_msg.get('direct_link'):
                            print("  **ENLACE DIRECTO VERIFICADO**")
                        else:
                            print("  **ERROR: Falta enlace directo**")
                    break
            except json.JSONDecodeError:
                continue
    
    print("\n" + "="*60)
    print("PRUEBA COMPLETADA")
    print("="*60)

if __name__ == "__main__":
    test_kafka_messages_with_links()
