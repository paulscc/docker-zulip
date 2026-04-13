#!/usr/bin/env python3
"""
Script simple para ver canales (topics) de Kafka y mostrar sus mensajes
"""

import json
import sys
import time
from datetime import datetime
from typing import Dict, List, Any
from kafka import KafkaConsumer, KafkaAdminClient
from kafka.admin import ConfigResourceType

class KafkaViewer:
    """Clase para visualizar topics y mensajes de Kafka"""
    
    def __init__(self, bootstrap_servers: str = "localhost:9092"):
        self.bootstrap_servers = bootstrap_servers
        self.consumer = None
        
    def conectar(self) -> bool:
        """Conectar a Kafka"""
        try:
            # Intentar crear un admin client para verificar conexión
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='kafka_viewer'
            )
            
            # Listar topics para verificar que funciona
            topics = admin_client.list_topics()
            admin_client.close()
            
            print(f"Conectado a Kafka en {self.bootstrap_servers}")
            return True
            
        except Exception as e:
            print(f"Error conectando a Kafka: {e}")
            return False
    
    def listar_topics(self) -> List[str]:
        """Listar todos los topics disponibles"""
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='kafka_viewer'
            )
            
            topics = admin_client.list_topics()
            admin_client.close()
            
            return list(topics)
            
        except Exception as e:
            print(f"Error listando topics: {e}")
            return []
    
    def mostrar_info_topic(self, topic_name: str):
        """Mostrar información detallada de un topic"""
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='kafka_viewer'
            )
            
            # Obtener metadata del topic
            cluster_metadata = admin_client.describe_cluster()
            topic_metadata = admin_client.describe_topics([topic_name])
            
            print(f"\n--- Información del Topic: {topic_name} ---")
            
            for tm in topic_metadata:
                if tm.topic == topic_name:
                    print(f"Particiones: {len(tm.partitions)}")
                    for partition in tm.partitions:
                        print(f"  Partición {partition.id}: Leader={partition.leader}, "
                              f"Replicas={partition.replicas}, ISR={partition.isr}")
            
            admin_client.close()
            
        except Exception as e:
            print(f"Error obteniendo info del topic {topic_name}: {e}")
    
    def ver_mensajes_topic(self, topic_name: str, max_mensajes: int = 10, desde_inicio: bool = False):
        """Ver mensajes de un topic específico"""
        try:
            # Configurar el consumer
            auto_offset_reset = 'earliest' if desde_inicio else 'latest'
            
            self.consumer = KafkaConsumer(
                topic_name,
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=lambda x: json.loads(x.decode('utf-8')) if x else None,
                key_deserializer=lambda k: k.decode('utf-8') if k else None,
                group_id='kafka_viewer_group',
                auto_offset_reset=auto_offset_reset,
                enable_auto_commit=False
            )
            
            print(f"\n--- Mensajes del Topic: {topic_name} ---")
            print(f"Mostrando últimos {max_mensajes} mensajes (desde_inicio={desde_inicio})")
            print("-" * 50)
            
            mensajes_recibidos = 0
            
            for message in self.consumer:
                mensajes_recibidos += 1
                
                # Formatear el mensaje
                timestamp = datetime.fromtimestamp(message.timestamp / 1000) if message.timestamp else "N/A"
                key = message.key if message.key else "sin_key"
                value = message.value if message.value else "sin_valor"
                
                print(f"[{timestamp}] Partition: {message.partition}, Offset: {message.offset}")
                print(f"Key: {key}")
                
                # Mostrar el valor de forma legible
                if isinstance(value, dict):
                    print("Value:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"Value: {value}")
                
                print("-" * 50)
                
                if mensajes_recibidos >= max_mensajes:
                    break
            
            if mensajes_recibidos == 0:
                print("No se encontraron mensajes en este topic")
            
            # Cerrar el consumer
            self.consumer.close()
            self.consumer = None
            
        except Exception as e:
            print(f"Error leyendo mensajes del topic {topic_name}: {e}")
            if self.consumer:
                self.consumer.close()
                self.consumer = None
    
    def ver_todos_los_topics(self, max_mensajes_por_topic: int = 5):
        """Ver mensajes de todos los topics disponibles"""
        topics = self.listar_topics()
        
        if not topics:
            print("No se encontraron topics")
            return
        
        print(f"\n=== TODOS LOS TOPICS ({len(topics)} encontrados) ===")
        
        for topic in topics:
            print(f"\n{topic}")
            self.ver_mensajes_topic(topic, max_mensajes_por_topic, desde_inicio=False)
            time.sleep(1)  # Pequeña pausa entre topics

def mostrar_menu():
    """Mostrar menú interactivo"""
    print("\n" + "="*60)
    print("           VISUALIZADOR DE KAFKA")
    print("="*60)
    print("1. Listar todos los topics")
    print("2. Ver información de un topic específico")
    print("3. Ver mensajes de un topic (últimos)")
    print("4. Ver mensajes de un topic (desde el inicio)")
    print("5. Ver mensajes de todos los topics")
    print("6. Salir")
    print("="*60)

def main():
    """Función principal"""
    viewer = KafkaViewer()
    
    # Verificar conexión
    if not viewer.conectar():
        print("No se pudo conectar a Kafka. Verifica que Kafka esté corriendo.")
        return
    
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (1-6): ").strip()
            
            if opcion == "1":
                topics = viewer.listar_topics()
                print(f"\nTopics encontrados ({len(topics)}):")
                for i, topic in enumerate(topics, 1):
                    print(f"  {i}. {topic}")
            
            elif opcion == "2":
                topic_name = input("Nombre del topic: ").strip()
                if topic_name:
                    viewer.mostrar_info_topic(topic_name)
                else:
                    print("Nombre de topic inválido")
            
            elif opcion == "3":
                topic_name = input("Nombre del topic: ").strip()
                if topic_name:
                    try:
                        max_msg = int(input("Número máximo de mensajes (default 10): ").strip() or "10")
                        viewer.ver_mensajes_topic(topic_name, max_msg, desde_inicio=False)
                    except ValueError:
                        viewer.ver_mensajes_topic(topic_name, 10, desde_inicio=False)
                else:
                    print("Nombre de topic inválido")
            
            elif opcion == "4":
                topic_name = input("Nombre del topic: ").strip()
                if topic_name:
                    try:
                        max_msg = int(input("Número máximo de mensajes (default 10): ").strip() or "10")
                        viewer.ver_mensajes_topic(topic_name, max_msg, desde_inicio=True)
                    except ValueError:
                        viewer.ver_mensajes_topic(topic_name, 10, desde_inicio=True)
                else:
                    print("Nombre de topic inválido")
            
            elif opcion == "5":
                try:
                    max_msg = int(input("Mensajes por topic (default 5): ").strip() or "5")
                    viewer.ver_todos_los_topics(max_msg)
                except ValueError:
                    viewer.ver_todos_los_topics(5)
            
            elif opcion == "6":
                print("¡Hasta luego!")
                break
            
            else:
                print("Opción inválida. Intenta nuevamente.")
        
        except KeyboardInterrupt:
            print("\n\nSaliendo...")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
