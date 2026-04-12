#!/usr/bin/env python3
"""
Llenar Canales con Mensajes de Prueba
Usa bots genéricos para llenar los 4 canales con mensajes
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class LlenadorCanales:
    def __init__(self):
        """Inicializar el llenador de canales"""
        self.server_url = "https://127.0.0.1.nip.io"
        
        # Usar el bot que sabemos que funciona
        self.bot_email = "aaa-bot@127.0.0.1.nip.io"
        self.bot_key = "f68mFE6Ihur5eNW58V2b3jE7cPvqOsWw"
        
        # Mensajes para cada canal
        self.mensajes_canales = {
            "comercio": [
                "Necesito revisar las estrategias de precios para Q2",
                "Los clientes están pidiendo más opciones de pago con criptomonedas",
                "Las ventas de este mes superaron los objetivos en un 25%",
                "Recordatorio: Reunión de ventas mañana a las 10am",
                "Nuevo competidor en el mercado, necesitamos analizar su estrategia",
                "Feedback positivo de los clientes sobre el nuevo sistema de facturación",
                "Propuesta: Implementar programa de lealtad para clientes frecuentes",
                "Análisis de mercado muestra oportunidad en segmento empresarial",
                "Necesitamos optimizar el proceso de envío para reducir costos",
                "Excelente trabajo del equipo de atención al cliente esta semana",
                "Las campañas de marketing digital están generando buen ROI",
                "Queremos expandirnos a mercados internacionales el próximo trimestre"
            ],
            "desarrollo": [
                "El nuevo deploy del sistema está listo para testing en producción",
                "Encontramos un bug crítico en el módulo de autenticación que necesita fix urgente",
                "La refactorización del código legacy mejoró el rendimiento en 40%",
                "Code review programado para hoy a las 3pm - revisar PR #234",
                "Tests unitarios cubriendo 85% del código base actual",
                "Propuesta de migración a microservicios para mejorar escalabilidad",
                "Security audit encontró 3 vulnerabilidades de prioridad media",
                "El nuevo sistema de CI/CD está reduciendo el tiempo de deploy en 50%",
                "Necesitamos actualizar las dependencias del proyecto esta semana",
                "Excelente colaboración entre equipos en el proyecto Alpha",
                "La documentación técnica necesita actualizarse",
                "Considerando adoptar TypeScript para nuevos proyectos"
            ],
            "equipo": [
                "Recordatorio: reunión de equipo mañana a las 10am",
                "Felicitaciones a Juan por su excelente presentación en la conferencia",
                "Team building: Actividad de escape room programada para este viernes",
                "Necesitamos volunteers para el comité de bienestar del equipo",
                "Evaluaciones de desempeño cierran el próximo viernes",
                "Nuevo miembro del equipo: Bienvenido Carlos al área de desarrollo",
                "Lunch & Learn próximo jueves: Tema 'Mejores prácticas de Git'",
                "Encuesta de satisfacción del equipo - por favor completar antes del viernes",
                "Reunión general de equipo hoy a las 9am en sala de conferencias",
                "Excelente colaboración entre equipos en el proyecto Beta",
                "Celebración del aniversario del equipo el próximo mes",
                "Nuevas políticas de trabajo remoto implementadas"
            ],
            "general": [
                "Mantenimiento programado del servidor este fin de semana - 12am-6am",
                "La cafetería estará cerrada por renovaciones del jueves al lunes",
                "Nuevo sistema de acceso a la oficina implementado - usar tarjetas RFID",
                "Recordatorio: Política de trabajo remoto actualizada - revisar intranet",
                "Nuevas reglas de estacionamiento a partir del próximo mes",
                "Seguridad: Simulacro de emergencia programado para el miércoles 2pm",
                "Actualización: Sistema de aire acondicionado reparado en piso 3",
                "Importante: Actualizar software antivirus en todos los equipos",
                "Feliz cumpleaños a Ana del equipo de marketing hoy",
                "Anuncio: Nuevo proveedor de servicios de internet contratado",
                "Recordatorio: Día festivo próximo lunes - oficina cerrada",
                "Nuevas directrices de seguridad implementadas en toda la empresa"
            ]
        }
    
    def enviar_mensaje(self, canal, topic, contenido):
        """Enviar un mensaje a un canal específico"""
        
        headers = {
            "Content-Type": "application/json"
        }
        auth = (self.bot_email, self.bot_key)
        
        payload = {
            "type": "stream",
            "to": canal,
            "topic": topic,
            "content": contenido
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/messages",
                headers=headers,
                json=payload,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                return True
            else:
                print(f"Error enviando mensaje: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Error enviando mensaje: {e}")
            return False
    
    def llenar_canal(self, canal):
        """Llenar un canal específico con mensajes de prueba"""
        
        print(f"\nLlenando canal #{canal}...")
        mensajes = self.mensajes_canales[canal]
        enviados = 0
        
        for i, mensaje in enumerate(mensajes, 1):
            contenido = f"{mensaje}\n\n*Mensaje de prueba #{i} - {datetime.now().strftime('%H:%M:%S')}*"
            
            if self.enviar_mensaje(canal, "general", contenido):
                enviados += 1
                print(f"  Mensaje {i}/{len(mensajes)} enviado")
            else:
                print(f"  Error enviando mensaje {i}")
            
            time.sleep(0.5)  # Pequeña pausa entre mensajes
        
        print(f"Canal #{canal}: {enviados}/{len(mensajes)} mensajes enviados")
        return enviados
    
    def llenar_todos_los_canales(self):
        """Llenar todos los canales con mensajes de prueba"""
        
        print("=== LLENANDO CANALES CON MENSAJES DE PRUEBA ===")
        print(f"Usando bot: {self.bot_email}")
        
        total_enviados = 0
        
        for canal in self.mensajes_canales.keys():
            enviados = self.llenar_canal(canal)
            total_enviados += enviados
            time.sleep(1)  # Pausa entre canales
        
        print(f"\nTotal de mensajes enviados: {total_enviados}")
        return total_enviados
    
    def verificar_canales(self):
        """Verificar que los mensajes aparezcan en los canales"""
        
        print("\n=== VERIFICANDO MENSAJES EN LOS CANALES ===")
        
        for canal in self.mensajes_canales.keys():
            print(f"\nVerificando canal #{canal}...")
            
            headers = {
                "Content-Type": "application/json"
            }
            auth = (self.bot_email, self.bot_key)
            
            params = {
                "stream": canal,
                "topic": "general",
                "narrow": json.dumps([
                    {"operator": "stream", "operand": canal},
                    {"operator": "topic", "operand": "general"}
                ])
            }
            
            try:
                response = requests.get(
                    f"{self.server_url}/api/v1/messages",
                    headers=headers,
                    params=params,
                    auth=auth,
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    messages = response.json().get("messages", [])
                    print(f"  Encontrados {len(messages)} mensajes en #{canal}")
                    
                    # Mostrar los últimos 2 mensajes
                    for i, msg in enumerate(messages[-2:], 1):
                        content = msg.get("content", "")[:80]
                        sender = msg.get("sender_full_name", "Unknown")
                        print(f"    {i}. {sender}: {content}...")
                else:
                    print(f"  Error verificando mensajes: {response.status_code}")
                    
            except Exception as e:
                print(f"  Error verificando canal: {e}")

def main():
    """Función principal"""
    
    llenador = LlenadorCanales()
    
    # Llenar todos los canales
    total_mensajes = llenador.llenar_todos_los_canales()
    
    if total_mensajes > 0:
        print(f"\n¡ÉXITO! Se enviaron {total_mensajes} mensajes a los 4 canales")
        
        # Verificar que los mensajes aparezcan
        llenador.verificar_canales()
        
        print("\n=== SIGUIENTES PASOS ===")
        print("1. Ahora los canales tienen mensajes")
        print("2. Inicia el publicador multi-bot:")
        print("   python publicador_multibot.py")
        print("3. El sistema detectará 10+ mensajes no leídos")
        print("4. Generará resúmenes automáticos con IA")
        print("5. Verás los resúmenes en #{canal}/resumen-{canal}")
        print("\n¡El sistema está listo para funcionar!")
        
    else:
        print("\nNo se pudieron enviar mensajes. Revisa la configuración.")

if __name__ == "__main__":
    main()
