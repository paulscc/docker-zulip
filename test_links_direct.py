#!/usr/bin/env python3
"""
Test script to send messages with links directly to Kafka using docker exec
"""

import subprocess
import json
from datetime import datetime

def send_test_message_with_links():
    """Send test message with direct links to Kafka"""
    
    # Create test message with links
    test_payload = {
        "trigger_type": "unread_messages",
        "timestamp": datetime.now().isoformat(),
        "stream": "test-enlaces",
        "topic": "prueba-directa",
        "messages": [
            {
                "id": 12345,
                "content": "Este es un mensaje de prueba con enlace directo a Zulip",
                "sender_full_name": "Usuario Test Enlaces",
                "timestamp": datetime.now().isoformat(),
                "direct_link": "https://localhost:443/#narrow/stream/123/topic/456/near/12345",
                "reactions": [],
                "flags": {}
            },
            {
                "id": 12346,
                "content": "Otro mensaje con enlace para probar el funcionamiento completo",
                "sender_full_name": "Usuario Test 2",
                "timestamp": datetime.now().isoformat(),
                "direct_link": "https://localhost:443/#narrow/stream/123/topic/456/near/12346",
                "reactions": [{"emoji": "thumbs_up", "count": 1}],
                "flags": {"read": False}
            },
            {
                "id": 12347,
                "content": "Tercer mensaje para tener suficiente contenido y generar un buen resumen con enlaces",
                "sender_full_name": "Usuario Test 3",
                "timestamp": datetime.now().isoformat(),
                "direct_link": "https://localhost:443/#narrow/stream/123/topic/456/near/12347",
                "reactions": [],
                "flags": {}
            }
        ],
        "message_count": 3,
        "webhook_token": "test-token-123",
        "server_url": "https://localhost:443"
    }
    
    # Convert to JSON string
    message_json = json.dumps(test_payload)
    
    print("Enviando mensaje con enlaces a Kafka...")
    print(f"Topic: zulip-unread-messages")
    print(f"Stream: {test_payload['stream']}")
    print(f"Topic: {test_payload['topic']}")
    print(f"Messages: {len(test_payload['messages'])}")
    
    # Send using docker exec
    cmd = [
        "docker", "exec", "opcion2-kafka-1",
        "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-unread-messages"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("SUCCESS: Mensaje enviado a Kafka con enlaces!")
            print("Verificando mensaje en Kafka...")
            
            # Read the message back
            read_cmd = [
                "docker", "exec", "opcion2-kafka-1",
                "kafka-console-consumer",
                "--bootstrap-server", "localhost:9092",
                "--topic", "zulip-unread-messages",
                "--from-beginning",
                "--timeout-ms", "5000"
            ]
            
            read_result = subprocess.run(read_cmd, capture_output=True, text=True, timeout=10)
            
            if read_result.returncode == 0 and read_result.stdout.strip():
                messages = read_result.stdout.strip().split('\n')
                print(f"Found {len(messages)} messages in Kafka topic")
                
                # Parse and display the last message
                for msg in reversed(messages):
                    try:
                        data = json.loads(msg)
                        if data.get('stream') == 'test-enlaces':
                            print("\nMensaje recuperado de Kafka:")
                            print(f"Stream: {data.get('stream')}")
                            print(f"Topic: {data.get('topic')}")
                            print(f"Message count: {data.get('message_count')}")
                            
                            for i, message in enumerate(data.get('messages', [])):
                                print(f"\n  Mensaje {i+1}:")
                                print(f"    Content: {message.get('content', '')}")
                                print(f"    Sender: {message.get('sender_full_name', 'N/A')}")
                                print(f"    Direct Link: {message.get('direct_link', 'NO LINK')}")
                                print(f"    Message ID: {message.get('id', 'N/A')}")
                                
                                if message.get('direct_link'):
                                    print("    **ENLACE DIRECTO INCLUIDO CORRECTAMENTE**")
                                else:
                                    print("    **ERROR: No se encontró enlace directo**")
                            break
                    except json.JSONDecodeError:
                        continue
            else:
                print("No se encontraron mensajes en el topic")
                
        else:
            print(f"ERROR: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    send_test_message_with_links()
