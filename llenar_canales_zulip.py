#!/usr/bin/env python3
"""
Llenar Canales de Zulip
Script para enviar mensajes de prueba a los 4 canales
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def enviar_mensajes_zulip():
    """Enviar mensajes de prueba a los 4 canales de Zulip"""
    
    # Configuración del bot (usando zzz-bot para enviar mensajes)
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "http://localhost"  # Usar HTTP en lugar de HTTPS
    
    canales_mensajes = {
        "comercio": [
            "¡Hola equipo! Necesitamos discutir la nueva estrategia de precios para Q2",
            "Los clientes están solicitando más opciones de pago con criptomonedas",
            "Las ventas de este mes han superado las expectativas en un 25%",
            "Recordatorio: Reunión de ventas mañana a las 10am",
            "Nuevo competidor en el mercado, necesitamos analizar su estrategia",
            "Feedback positivo de los clientes sobre el nuevo sistema de facturación",
            "Propuesta: Implementar programa de lealtad para clientes frecuentes",
            "Análisis de mercado muestra oportunidad en segmento empresarial",
            "Necesitamos optimizar el proceso de envío para reducir costos",
            "Excelente trabajo del equipo de atención al cliente esta semana"
        ],
        "desarrollo": [
            "Deploy del nuevo módulo de autenticación completado exitosamente",
            "Bug crítico encontrado en el procesador de pagos - necesita fix urgente",
            "La refactorización del código legacy mejoró el rendimiento 40%",
            "Nuevo framework frontend propuesto para el próximo sprint",
            "Code review programado para hoy a las 3pm - revisar PR #234",
            "Tests unitarios cubriendo 85% del código base actual",
            "Propuesta de migración a microservicios para mejorar escalabilidad",
            "Security audit encontró 3 vulnerabilidades de prioridad media",
            "Necesitamos actualizar las dependencias del proyecto esta semana",
            "El nuevo sistema de CI/CD está reduciendo el tiempo de deploy en 50%"
        ],
        "equipo": [
            "¡Felicitaciones a María por su excelente presentación en la conferencia!",
            "Team building: Actividad de escape room programada para este viernes",
            "Necesitamos voluntarios para el comité de bienestar del equipo",
            "Recordatorio: Evaluaciones de desempeño cierran el próximo viernes",
            "Nuevo miembro del equipo: Bienvenido Carlos al área de desarrollo",
            "Solicitud de vacaciones: Por favor enviar para planificación Q2",
            "Lunch & Learn próximo jueves: Tema 'Mejores prácticas de Git'",
            "Encuesta de satisfacción del equipo - por favor completar antes del viernes",
            "Reunión general de equipo mañana a las 9am en sala de conferencias",
            "Excelente colaboración entre equipos en el proyecto Alpha"
        ],
        "general": [
            "Mantenimiento programado del servidor este fin de semana - 12am-6am",
            "La cafetería estará cerrada por renovaciones del jueves al lunes",
            "Nuevo sistema de acceso a la oficina implementado - usar tarjetas RFID",
            "Recordatorio: Política de trabajo remoto actualizada - revisar intranet",
            "Estacionamiento: Nuevas reglas a partir del próximo mes",
            "Seguridad: Simulacro de emergencia programado para el miércoles 2pm",
            "Actualización: Sistema de aire acondicionado reparado en piso 3",
            "Importante: Actualizar software antivirus en todos los equipos",
            "Feliz cumpleaños a Ana del equipo de marketing!",
            "Anuncio: Nuevo proveedor de servicios de internet contratado"
        ]
    }
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    total_enviados = 0
    
    for canal, mensajes in canales_mensajes.items():
        print(f"Enviando mensajes al canal #{canal}...")
        
        for i, mensaje in enumerate(mensajes):
            payload = {
                "type": "stream",
                "to": canal,
                "topic": "general",
                "content": f"{mensaje}\n\n*Mensaje #{i+1} de prueba - {datetime.now().strftime('%H:%M:%S')}*"
            }
            
            try:
                response = requests.post(
                    f"{server_url}/api/v1/messages",
                    headers=headers,
                    json=payload,
                    verify=False
                )
                
                if response.status_code == 200:
                    total_enviados += 1
                    print(f"  Mensaje {i+1} enviado exitosamente")
                else:
                    print(f"  Error enviando mensaje {i+1}: {response.status_code}")
                
                time.sleep(0.5)  # Pequeña pausa entre mensajes
                
            except Exception as e:
                print(f"  Error enviando mensaje {i+1}: {e}")
        
        print(f"Completado canal #{canal}\n")
    
    print(f"Total de mensajes enviados: {total_enviados}")
    return total_enviados

def verificar_canales():
    """Verificar que los canales existan y tengan mensajes"""
    
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "http://localhost"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(f"{server_url}/api/v1/streams", headers=headers, verify=False)
        
        if response.status_code == 200:
            streams = response.json().get("streams", [])
            print(f"Streams encontrados: {len(streams)}")
            
            for stream in streams:
                if stream["name"] in ["comercio", "desarrollo", "equipo", "general"]:
                    print(f"  - #{stream['name']}: {stream.get('description', 'Sin descripción')}")
        else:
            print(f"Error obteniendo streams: {response.status_code}")
            
    except Exception as e:
        print(f"Error verificando canales: {e}")

def main():
    """Función principal"""
    
    print("=== LLENANDO CANALES DE ZULIP ===")
    print("Verificando canales existentes...")
    verificar_canales()
    
    print("\nEnviando mensajes de prueba...")
    total = enviar_mensajes_zulip()
    
    print(f"\n=== COMPLETADO ===")
    print(f"Se enviaron {total} mensajes a los 4 canales")
    print("\nLos canales ahora deberían tener contenido:")
    print("- #comercio: 10 mensajes sobre negocios y ventas")
    print("- #desarrollo: 10 mensajes sobre tecnología y desarrollo")
    print("- #equipo: 10 mensajes sobre colaboración y equipo")
    print("- #general: 10 mensajes sobre anuncios y operaciones")
    
    print("\nEl sistema de webhooks debería:")
    print("1. Detectar los mensajes no leídos")
    print("2. Enviarlos a Kafka para procesamiento")
    print("3. Generar resúmenes con gemma2:2b")
    print("4. Publicar resúmenes en los canales correspondientes")

if __name__ == "__main__":
    main()
