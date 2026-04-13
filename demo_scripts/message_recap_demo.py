#!/usr/bin/env python3
"""
Message Recap Demo Script
Script para generar video demostrativo de la funcionalidad Message Recap
"""

import time
import json
import requests
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

class MessageRecapDemo:
    def __init__(self):
        """Inicializar el demo de Message Recap"""
        self.base_url = "http://localhost:5001"
        self.frontend_url = "http://localhost:5000"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configurar Selenium WebDriver para grabación"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        # Para grabación (requiere configuración adicional)
        # chrome_options.add_argument("--enable-features=VizDisplayCompositor")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def start_backend(self):
        """Iniciar el backend de Message Recap"""
        print("Iniciando backend de Message Recap...")
        try:
            # Verificar si el backend está corriendo
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("Backend ya está corriendo")
                return True
        except:
            print("Backend no está corriendo. Por favor inicia manualmente:")
            print("python message_recap_backend.py")
            return False
    
    def generate_test_data(self):
        """Generar datos de prueba para el demo"""
        print("Generando datos de prueba...")
        
        # Crear mensajes de prueba
        test_messages = [
            {
                "id": 1001,
                "content": "Bienvenidos al equipo del proyecto Alpha! Vamos a discutir los objetivos para este trimestre.",
                "sender_full_name": "Maria Rodriguez",
                "timestamp": time.time() - 3600,
                "stream": "general",
                "subject": "proyecto-alpha",
                "direct_link": "http://localhost:443/#narrow/stream/general/topic/proyecto-alpha/near/1001"
            },
            {
                "id": 1002,
                "content": "Gracias Maria. Mi objetivo principal es completar la migración de la base de datos antes del 15 de marzo.",
                "sender_full_name": "Carlos Chen",
                "timestamp": time.time() - 3000,
                "stream": "general",
                "subject": "proyecto-alpha",
                "direct_link": "http://localhost:443/#narrow/stream/general/topic/proyecto-alpha/near/1002"
            },
            {
                "id": 1003,
                "content": "Yo me encargaré del frontend. Necesito revisar los requisitos de UX con el equipo de diseño.",
                "sender_full_name": "Ana Martinez",
                "timestamp": time.time() - 2400,
                "stream": "general",
                "subject": "proyecto-alpha",
                "direct_link": "http://localhost:443/#narrow/stream/general/topic/proyecto-alpha/near/1003"
            },
            {
                "id": 1004,
                "content": "Importante: La reunión de seguimiento es mañana a las 10 AM. No olviden preparar sus reportes de progreso.",
                "sender_full_name": "David Kim",
                "timestamp": time.time() - 1800,
                "stream": "general",
                "subject": "proyecto-alpha",
                "direct_link": "http://localhost:443/#narrow/stream/general/topic/proyecto-alpha/near/1004"
            },
            {
                "id": 1005,
                "content": "He actualizado la documentación técnica. Ya está disponible en el repositorio del proyecto.",
                "sender_full_name": "Laura Silva",
                "timestamp": time.time() - 1200,
                "stream": "general",
                "subject": "proyecto-alpha",
                "direct_link": "http://localhost:443/#narrow/stream/general/topic/proyecto-alpha/near/1005"
            }
        ]
        
        return test_messages
    
    def record_demo_video(self):
        """Grabar el video demostrativo"""
        print("Iniciando grabación del video demo...")
        
        try:
            # Paso 1: Abrir la interfaz web
            print("Paso 1: Abriendo interfaz de Message Recap")
            self.driver.get(f"{self.frontend_url}/templates/message_recap.html")
            time.sleep(3)
            
            # Paso 2: Llenar el formulario
            print("Paso 2: Completando formulario de usuario")
            
            # Esperar a que cargue el formulario
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "user-email"))
            )
            
            # Ingresar email de usuario
            email_input = self.driver.find_element(By.ID, "user-email")
            email_input.clear()
            email_input.send_keys("demo@zulip.com")
            time.sleep(2)
            
            # Seleccionar canal
            stream_select = self.driver.find_element(By.ID, "stream-select")
            stream_select.send_keys("general")
            time.sleep(2)
            
            # Paso 3: Generar resumen
            print("Paso 3: Generando resumen de mensajes")
            
            generate_btn = self.driver.find_element(By.ID, "generate-recap-btn")
            generate_btn.click()
            
            # Esperar a que se muestre el loading
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "loading-section"))
            )
            time.sleep(5)  # Simular tiempo de procesamiento
            
            # Paso 4: Mostrar resultados
            print("Paso 4: Mostrando resultados del resumen")
            
            # Esperar a que aparezcan los resultados
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "results-section"))
            )
            time.sleep(3)
            
            # Hacer scroll para ver todos los resultados
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Paso 5: Mostrar preferencias
            print("Paso 5: Mostrando panel de preferencias")
            
            # Scroll hacia abajo para mostrar preferencias
            preferences_section = self.driver.find_element(By.XPATH, "//h2[contains(text(),'Preferencias de Resumen')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", preferences_section)
            time.sleep(3)
            
            # Paso 6: Finalizar demo
            print("Paso 6: Finalizando demostración")
            
            # Volver al inicio
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            print("Video demostrativo completado!")
            
        except Exception as e:
            print(f"Error durante la grabación: {e}")
    
    def create_demo_screenshots(self):
        """Crear capturas de pantalla para el demo"""
        print("Creando capturas de pantalla...")
        
        screenshots = [
            ("01_login", "user-email"),
            ("02_form_complete", "generate-recap-btn"),
            ("03_loading", "loading-section"),
            ("04_results", "results-section"),
            ("05_summary", "summary-content"),
            ("06_messages", "messages-list"),
            ("07_preferences", "preferences")
        ]
        
        try:
            for name, element_id in screenshots:
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    screenshot_path = f"demo_screenshots/message_recap_{name}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Captura guardada: {screenshot_path}")
                    
                except Exception as e:
                    print(f"Error capturando {name}: {e}")
                    
        except Exception as e:
            print(f"Error general en capturas: {e}")
    
    def generate_demo_script(self):
        """Generar script narrado para el video"""
        script_content = """
# Message Recap Demo Script

## Intro (0:00 - 0:15)
"Hola y bienvenidos al demo de Message Recap, una funcionalidad de IA para Zulip que genera resúmenes automáticos de mensajes no leídos con enlaces directos a los mensajes originales."

## Paso 1: Acceso a la Interfaz (0:15 - 0:30)
"Primero, accedemos a la interfaz web de Message Recap. Aquí vemos un diseño limpio y moderno con Tailwind CSS."

## Paso 2: Configuración de Usuario (0:30 - 0:45)
"Ahora ingresamos el email del usuario y seleccionamos el canal que queremos analizar. Podemos dejar el canal en blanco para analizar todos los mensajes no leídos."

## Paso 3: Generación de Resumen (0:45 - 1:15)
"Hacemos clic en 'Generar Resumen' y el sistema comienza a procesar los mensajes usando IA. Vemos el indicador de carga mientras el sistema analiza los mensajes con Gemini Pro u Ollama."

## Paso 4: Resultados del Resumen (1:15 - 2:00)
"¡Listo! El sistema ha generado un resumen estructurado con:
- Resumen general de la conversación
- Puntos clave identificados
- Acciones requeridas
- Enlaces directos a cada mensaje original"

## Paso 5: Navegación a Mensajes (2:00 - 2:30)
"Cada mensaje tiene un enlace directo que nos lleva exactamente a ese mensaje en Zulip. Esto es muy útil para encontrar contexto específico rápidamente."

## Paso 6: Configuración de Preferencias (2:30 - 3:00)
"Los usuarios pueden configurar sus preferencias como frecuencia de resúmenes, modelo de IA a usar, y canales a monitorear."

## Conclusión (3:00 - 3:15)
"Message Recap es una herramienta poderosa que ayuda a los usuarios a mantenerse actualizados con conversaciones largas, ahorrando tiempo y mejorando la productividad."

## Características Técnicas
- Backend Flask con Python
- Integración con Gemini Pro y Ollama
- Kafka para procesamiento asíncrono
- Frontend responsive con Socket.io
- Enlaces directos a mensajes de Zulip
"""
        
        with open("demo_scripts/message_recap_script.txt", "w") as f:
            f.write(script_content)
        
        print("Script narrado guardado en demo_scripts/message_recap_script.txt")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()
    
    def run_demo(self):
        """Ejecutar el demo completo"""
        try:
            print("=== Message Recap Demo ===")
            
            # Verificar backend
            if not self.start_backend():
                return
            
            # Generar datos de prueba
            test_data = self.generate_test_data()
            
            # Grabar video demo
            self.record_demo_video()
            
            # Crear capturas de pantalla
            self.create_demo_screenshots()
            
            # Generar script narrado
            self.generate_demo_script()
            
            print("Demo completado exitosamente!")
            print("Archivos generados:")
            print("- Video: (requiere software de grabación)")
            print("- Screenshots: demo_screenshots/")
            print("- Script: demo_scripts/message_recap_script.txt")
            
        except Exception as e:
            print(f"Error en el demo: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = MessageRecapDemo()
    demo.run_demo()
