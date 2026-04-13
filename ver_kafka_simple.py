#!/usr/bin/env python3
"""
Script simple y rápido para ver topics y mensajes de Kafka
"""

import json
import sys
from kafka import KafkaConsumer, KafkaAdminClient

def ver_topics_y_mensajes():
    """Función principal que muestra todos los topics y sus mensajes"""
    bootstrap_servers = "localhost:9092"
    
    try:
        # Conectar y listar topics
        print("Conectando a Kafka...")
        admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers,
            client_id='kafka_viewer'
        )
        
        topics = admin_client.list_topics()
        admin_client.close()
        
        print(f"\nTopics encontrados: {len(topics)}")
        print("=" * 50)
        
        if not topics:
            print("No se encontraron topics")
            return
        
        # Para cada topic, mostrar algunos mensajes
        for topic in topics:
            print(f"\n--- TOPIC: {topic} ---")
            
            try:
                consumer = KafkaConsumer(
                    topic,
                    bootstrap_servers=bootstrap_servers,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                    key_deserializer=lambda k: k.decode('utf-8') if k else None,
                    group_id='viewer_group',
                    auto_offset_reset='latest',
                    consumer_timeout_ms=2000  # Timeout después de 2 segundos sin mensajes
                )
                
                mensajes = []
                for message in consumer:
                    mensajes.append({
                        'partition': message.partition,
                        'offset': message.offset,
                        'key': message.key,
                        'value': message.value,
                        'timestamp': message.timestamp
                    })
                    
                    # Limitar a 5 mensajes por topic
                    if len(mensajes) >= 5:
                        break
                
                consumer.close()
                
                if mensajes:
                    for i, msg in enumerate(mensajes, 1):
                        print(f"  Mensaje {i}:")
                        print(f"    Partition: {msg['partition']}, Offset: {msg['offset']}")
                        if msg['key']:
                            print(f"    Key: {msg['key']}")
                        if msg['value']:
                            if isinstance(msg['value'], dict):
                                print("    Value:")
                                for k, v in msg['value'].items():
                                    print(f"      {k}: {v}")
                            else:
                                print(f"    Value: {msg['value']}")
                        print()
                else:
                    print("  (No hay mensajes recientes)")
                
            except Exception as e:
                print(f"  Error leyendo mensajes: {e}")
        
        print("=" * 50)
        print("Listo!")
        
    except Exception as e:
        print(f"Error general: {e}")
        print("Asegúrate de que Kafka esté corriendo en localhost:9092")

if __name__ == "__main__":
    ver_topics_y_mensajes()
