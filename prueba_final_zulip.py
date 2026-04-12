#!/usr/bin/env python3
"""
Prueba Final de Zulip
Envía mensajes de prueba y verifica que los resúmenes se publiquen
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def probar_conexion_zulip():
    """Probar conexión con Zulip"""
    try:
        response = requests.get(
            "https://localhost:443/api/v1/server_settings",
            verify=False,
            timeout=10
        )
        
        if response.status_code == 200:
            settings = response.json()
            print(f"Conexión exitosa con Zulip v{settings.get('zulip_version')}")
            print(f"Realm: {settings.get('realm_name')}")
            return True
        else:
            print(f"Error de conexión: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error de conexión: {e}")
        return False

def enviar_mensajes_prueba():
    """Enviar mensajes de prueba a los canales"""
    
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "https://localhost:443"
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")  # HTTP Basic Auth con API key como username
    
    mensajes = {
        "comercio": [
            "Nueva estrategia de precios implementada con éxito",
            "Los clientes reportan satisfacción con las nuevas opciones de pago",
            "Ventas del mes superan objetivos en 20%"
        ],
        "desarrollo": [
            "Deploy del sistema completado sin errores",
            "Bug crítico de autenticación resuelto",
            "Performance mejorado en 35% con optimizaciones"
        ],
        "equipo": [
            "Reunión de equipo programada para mañana 10am",
            "Felicitaciones al equipo por el excelente trabajo",
            "Nuevo miembro se integra perfectamente al equipo"
        ],
        "general": [
            "Mantenimiento del servidor completado exitosamente",
            "Nuevas políticas de trabajo remoto implementadas",
            "Celebración del aniversario de la empresa este viernes"
        ]
    }
    
    total_enviados = 0
    
    for canal, msgs in mensajes.items():
        print(f"\nEnviando mensajes al canal #{canal}...")
        
        for i, msg in enumerate(msgs, 1):
            payload = {
                "type": "stream",
                "to": canal,
                "topic": "general",
                "content": f"{msg}\n\n*Mensaje de prueba #{i} - {datetime.now().strftime('%H:%M:%S')}*"
            }
            
            try:
                response = requests.post(
                    f"{server_url}/api/v1/messages",
                    headers=headers,
                    json=payload,
                    auth=auth,
                    verify=False,
                    timeout=10
                )
                
                if response.status_code == 200:
                    total_enviados += 1
                    print(f"  Mensaje {i} enviado exitosamente")
                else:
                    print(f"  Error mensaje {i}: {response.status_code} - {response.text}")
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"  Error mensaje {i}: {e}")
    
    print(f"\nTotal mensajes enviados: {total_enviados}")
    return total_enviados > 0

def verificar_resumenes():
    """Verificar que los resúmenes aparezcan en los canales"""
    
    print("\nVerificando aparición de resúmenes...")
    print("Esperando 15 segundos para procesamiento...")
    
    time.sleep(15)
    
    api_key = "tjsPrruzMZl7eo3uDvQtau1AqUv1ZS9m"
    server_url = "https://localhost:443"
    
    headers = {
        "Content-Type": "application/json"
    }
    auth = (api_key, "")  # HTTP Basic Auth con API key como username
    
    canales = ["comercio", "desarrollo", "equipo", "general"]
    
    for canal in canales:
        print(f"\nVerificando canal #{canal}...")
        
        # Buscar resúmenes en el canal
        params = {
            "stream": canal,
            "topic": "resumen-general",
            "narrow": json.dumps([
                {"operator": "stream", "operand": canal},
                {"operator": "topic", "operand": "resumen-general"}
            ])
        }
        
        try:
            response = requests.get(
                f"{server_url}/api/v1/messages",
                headers=headers,
                params=params,
                auth=auth,
                verify=False,
                timeout=10
            )
            
            if response.status_code == 200:
                messages = response.json().get("messages", [])
                print(f"  Encontrados {len(messages)} resúmenes en #{canal}/resumen-general")
                
                for i, msg in enumerate(messages[-2:], 1):  # Mostrar últimos 2
                    content = msg.get("content", "")[:100]
                    print(f"    {i}. {content}...")
                    
            else:
                print(f"  Error verificando resúmenes: {response.status_code}")
                
        except Exception as e:
            print(f"  Error verificando resúmenes: {e}")

def main():
    """Función principal"""
    
    print("=== PRUEBA FINAL DEL SISTEMA ZULIP ===")
    print("Verificando conexión y enviando mensajes de prueba\n")
    
    # Probar conexión
    if not probar_conexion_zulip():
        print("No se puede conectar a Zulip. Abortando prueba.")
        return
    
    # Enviar mensajes
    if enviar_mensajes_prueba():
        print("\nMensajes enviados exitosamente")
        
        # Verificar resúmenes
        verificar_resumenes()
        
        print("\n=== RESULTADO ===")
        print("El sistema debería:")
        print("1. Detectar los mensajes enviados")
        print("2. Enviarlos a Kafka para procesamiento")
        print("3. Generar resúmenes con gemma2:2b")
        print("4. Publicar resúmenes en #{canal}/resumen-general")
        print("\nRevisa los canales en Zulip para ver los resúmenes generados.")
        
    else:
        print("\nNo se pudieron enviar mensajes. Revisa la configuración.")

if __name__ == "__main__":
    main()
