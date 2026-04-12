#!/usr/bin/env python3
"""
Simulador de Usuarios Activos
Envía mensajes cada 10 segundos por usuario con inicios aleatorios
"""

import json
import subprocess
import time
import random
import threading
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

class SimuladorUsuarios:
    def __init__(self):
        """Inicializar el simulador de usuarios"""
        self.server_url = "https://127.0.0.1.nip.io"
        self.bot_email = "aaa-bot@127.0.0.1.nip.io"
        self.bot_key = "f68mFE6Ihur5eNW58V2b3jE7cPvqOsWw"
        
        # Usuarios simulados
        self.usuarios = {
            "comercio": [
                {"nombre": "Ana García", "rol": "Gerente de Ventas"},
                {"nombre": "Carlos Ruiz", "rol": "Analista de Mercado"},
                {"nombre": "María López", "rol": "Especialista en Marketing"},
                {"nombre": "Pedro Martín", "rol": "Coordinador de Logística"}
            ],
            "desarrollo": [
                {"nombre": "Juan Pérez", "rol": "Desarrollador Senior"},
                {"nombre": "Laura Sánchez", "rol": "QA Engineer"},
                {"nombre": "Diego Fernández", "rol": "DevOps Engineer"},
                {"nombre": "Sofía Castro", "rol": "Tech Lead"}
            ],
            "equipo": [
                {"nombre": "Roberto Díaz", "rol": "HR Manager"},
                {"nombre": "Elena Torres", "rol": "Team Lead"},
                {"nombre": "Miguel Ángel", "rol": "Scrum Master"},
                {"nombre": "Lucía Vargas", "rol": "Product Owner"}
            ],
            "general": [
                {"nombre": "Administración", "rol": "Sistema"},
                {"nombre": "Soporte IT", "rol": "Soporte"},
                {"nombre": "Facilities", "rol": "Instalaciones"},
                {"nombre": "Seguridad", "rol": "Seguridad"}
            ]
        }
        
        # Mensajes por canal
        self.mensajes_canales = {
            "comercio": [
                "Necesito revisar las métricas de ventas del último trimestre",
                "Los clientes están solicitando más opciones de pago digital",
                "La campaña de marketing está generando excelentes resultados",
                "Debemos optimizar el proceso de envío para reducir costos",
                "Necesito feedback sobre la nueva estrategia de precios",
                "El equipo de atención al cliente está trabajando excelente",
                "Queremos lanzar una nueva línea de productos el próximo mes",
                "El análisis de competencia muestra oportunidades interesantes",
                "Necesito aprobar el presupuesto para el próximo trimestre",
                "Los clientes están muy satisfechos con el nuevo sistema",
                "Debemos considerar expandirnos a mercados internacionales",
                "La retroalimentación del cliente es muy positiva"
            ],
            "desarrollo": [
                "El deploy del nuevo módulo está listo para producción",
                "Encontré un bug crítico en el sistema de autenticación",
                "La refactorización mejoró el rendimiento en un 40%",
                "Necesito hacer code review del PR #234",
                "Los tests unitarios cubren el 85% del código",
                "Propongo migrar a microservicios para mejorar escalabilidad",
                "El security audit encontró 3 vulnerabilidades medias",
                "El nuevo CI/CD reduce el tiempo de deploy en 50%",
                "Debemos actualizar las dependencias esta semana",
                "Excelente colaboración en el proyecto Alpha",
                "La documentación técnica necesita actualizarse",
                "Considero que deberíamos adoptar TypeScript"
            ],
            "equipo": [
                "Recordatorio: reunión de equipo mañana a las 10am",
                "Felicitaciones por el excelente trabajo esta semana",
                "Team building: escape room el viernes",
                "Necesitamos volunteers para el comité de bienestar",
                "Las evaluaciones de desempeño cierran el viernes",
                "Bienvenido al nuevo miembro del equipo",
                "Lunch & Learn sobre Git el jueves",
                "Por favor completen la encuesta de satisfacción",
                "Excelente colaboración entre equipos",
                "Celebración del aniversario del equipo",
                "Nuevas políticas de trabajo remoto",
                "El ambiente de trabajo es excelente"
            ],
            "general": [
                "Mantenimiento del servidor este fin de semana",
                "La cafetería estará cerrada por renovaciones",
                "Nuevo sistema de acceso con tarjetas RFID",
                "Política de trabajo remoto actualizada",
                "Nuevas reglas de estacionamiento",
                "Simulacro de emergencia el miércoles",
                "Aire acondicionado reparado en piso 3",
                "Actualicen el antivirus en sus equipos",
                "Feliz cumpleaños Ana del equipo de marketing",
                "Nuevo proveedor de internet contratado",
                "Día festivo próximo lunes",
                "Nuevas directrices de seguridad"
            ]
        }
        
        self.threads_activos = []
        self.detener = False
    
    def enviar_mensaje_simulado(self, canal, usuario, mensaje):
        """Simular el envío de un mensaje a Kafka"""
        
        # Crear mensaje en formato Zulip
        mensaje_zulip = {
            "sender_full_name": f"{usuario['nombre']} ({usuario['rol']})",
            "content": mensaje,
            "timestamp": datetime.now().isoformat(),
            "stream": canal,
            "topic": "general"
        }
        
        # Enviar a Kafka como si fuera un mensaje de Zulip
        payload = {
            "trigger_type": "unread_messages",
            "timestamp": datetime.now().isoformat(),
            "stream": canal,
            "topic": "general",
            "messages": [mensaje_zulup],
            "message_count": 1,
            "webhook_token": "zj26mcSxoxqSra6pjwGzPftB5fz2CA8I"
        }
        
        # Enviar a Kafka
        message_json = json.dumps(payload)
        cmd = [
            "docker", "exec", "opcion2-kafka-1",
            "bash", "-c", f"echo '{message_json}' | kafka-console-producer --bootstrap-server localhost:9092 --topic zulip-unread-messages"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                timestamp = datetime.now().strftime('%H:%M:%S')
                print(f"[{timestamp}] {canal}: {usuario['nombre']} - {mensaje[:50]}...")
                return True
            else:
                print(f"Error enviando mensaje a Kafka: {result.stderr}")
                return False
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False
    
    def usuario_activo(self, canal, usuario):
        """Hilo que simula un usuario activo enviando mensajes"""
        
        mensajes = self.mensajes_canales[canal].copy()
        random.shuffle(mensajes)
        
        # Inicio aleatorio (0-10 segundos)
        inicio_aleatorio = random.uniform(0, 10)
        time.sleep(inicio_aleatorio)
        
        mensaje_count = 0
        
        while not self.detener and mensajes:
            # Enviar mensaje
            mensaje = mensajes.pop(0)
            self.enviar_mensaje_simulado(canal, usuario, mensaje)
            mensaje_count += 1
            
            # Esperar 10 segundos antes del siguiente mensaje
            time.sleep(10)
        
        print(f"{usuario['nombre']} ({canal}): Enviados {mensaje_count} mensajes")
    
    def iniciar_simulacion(self):
        """Iniciar la simulación de usuarios activos"""
        
        print("=== SIMULADOR DE USUARIOS ACTIVOS ===")
        print("Enviando mensajes cada 10 segundos por usuario")
        print("Inicios aleatorios entre 0-10 segundos\n")
        
        # Crear hilos para cada usuario
        for canal, usuarios in self.usuarios.items():
            for usuario in usuarios:
                thread = threading.Thread(
                    target=self.usuario_activo,
                    args=(canal, usuario)
                )
                thread.daemon = True
                self.threads_activos.append(thread)
                thread.start()
        
        # Mostrar estadísticas
        self.mostrar_estadisticas()
        
        # Esperar a que todos terminen
        try:
            while any(thread.is_alive() for thread in self.threads_activos):
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nDeteniendo simulación...")
            self.detener = True
        
        print("\nSimulación completada")
    
    def mostrar_estadisticas(self):
        """Mostrar estadísticas en tiempo real"""
        
        while not self.detener:
            try:
                # Verificar mensajes en Kafka
                cmd = [
                    "docker", "exec", "opcion2-kafka-1",
                    "kafka-console-consumer",
                    "--bootstrap-server", "localhost:9092",
                    "--topic", "zulip-unread-messages",
                    "--from-beginning",
                    "--timeout-ms", "2000"
                ]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    mensajes = result.stdout.strip().split('\n')
                    timestamp = datetime.now().strftime('%H:%M:%S')
                    print(f"[{timestamp}] Total mensajes en Kafka: {len(mensajes)}")
                
                time.sleep(30)  # Mostrar estadísticas cada 30 segundos
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error en estadísticas: {e}")
                time.sleep(30)

def main():
    """Función principal"""
    
    simulador = SimuladorUsuarios()
    
    try:
        simulador.iniciar_simulacion()
    except KeyboardInterrupt:
        print("\nSimulación detenida por usuario")

if __name__ == "__main__":
    main()
