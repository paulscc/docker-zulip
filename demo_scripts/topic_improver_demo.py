#!/usr/bin/env python3
"""
Topic Title Improver Demo Script
Script para generar video demostrativo de la funcionalidad Topic Title Improver
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

class TopicImproverDemo:
    def __init__(self):
        """Inicializar el demo de Topic Title Improver"""
        self.base_url = "http://localhost:5002"
        self.frontend_url = "http://localhost:5000"
        self.driver = None
        self.setup_driver()
    
    def setup_driver(self):
        """Configurar Selenium WebDriver para grabación"""
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-extensions")
        
        self.driver = webdriver.Chrome(options=chrome_options)
    
    def start_backend(self):
        """Iniciar el backend de Topic Title Improver"""
        print("Iniciando backend de Topic Title Improver...")
        try:
            # Verificar si el backend está corriendo
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                print("Backend ya está corriendo")
                return True
        except:
            print("Backend no está corriendo. Por favor inicia manualmente:")
            print("python topic_title_improver_backend.py")
            return False
    
    def generate_test_topic_data(self):
        """Generar datos de prueba para el demo"""
        print("Generando datos de prueba para análisis de tema...")
        
        # Crear mensajes que muestran deriva de tema
        test_messages = [
            {
                "id": 2001,
                "content": "Comenzando la planificación del proyecto de migración a la nube. Necesitamos definir el stack tecnológico.",
                "sender_full_name": "Roberto Diaz",
                "timestamp": time.time() - 7200,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2001"
            },
            {
                "id": 2002,
                "content": "Para la migración, sugiero usar AWS con ECS para contenedores. Es más escalable que soluciones on-premise.",
                "sender_full_name": "Sofia Martinez",
                "timestamp": time.time() - 6600,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2002"
            },
            {
                "id": 2003,
                "content": "Por cierto, hablando de contenedores, ¿alguien ha trabajado con Kubernetes? Es mucho mejor que Docker solo.",
                "sender_full_name": "Luis Chen",
                "timestamp": time.time() - 5400,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2003"
            },
            {
                "id": 2004,
                "content": "Kubernetes es excelente para orquestación. Yo lo uso para microservicios con auto-scaling.",
                "sender_full_name": "Ana Silva",
                "timestamp": time.time() - 4800,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2004"
            },
            {
                "id": 2005,
                "content": "La arquitectura de microservicios requiere buen diseño de APIs. GraphQL es mejor que REST para casos complejos.",
                "sender_full_name": "Carlos Kim",
                "timestamp": time.time() - 4200,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2005"
            },
            {
                "id": 2006,
                "content": "Volviendo al tema original, necesitamos definir el roadmap de migración. ¿Cuándo empezamos?",
                "sender_full_name": "Roberto Diaz",
                "timestamp": time.time() - 3000,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2006"
            },
            {
                "id": 2007,
                "content": "Propongo empezar con los servicios no críticos. Podemos usar feature flags para rollout gradual.",
                "sender_full_name": "Maria Rodriguez",
                "timestamp": time.time() - 2400,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2007"
            },
            {
                "id": 2008,
                "content": "Importante: necesitamos actualizar la documentación de arquitectura antes de la migración.",
                "sender_full_name": "David Liu",
                "timestamp": time.time() - 1800,
                "stream": "development",
                "subject": "migracion-nube",
                "direct_link": "http://localhost:443/#narrow/stream/development/topic/migracion-nube/near/2008"
            }
        ]
        
        return test_messages
    
    def record_demo_video(self):
        """Grabar el video demostrativo"""
        print("Iniciando grabación del video demo...")
        
        try:
            # Paso 1: Abrir la interfaz web
            print("Paso 1: Abriendo interfaz de Topic Title Improver")
            self.driver.get(f"{self.frontend_url}/templates/topic_improver.html")
            time.sleep(3)
            
            # Paso 2: Llenar el formulario de análisis
            print("Paso 2: Completando formulario de análisis de tema")
            
            # Esperar a que cargue el formulario
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "stream-input"))
            )
            
            # Ingresar canal
            stream_input = self.driver.find_element(By.ID, "stream-input")
            stream_input.clear()
            stream_input.send_keys("development")
            time.sleep(2)
            
            # Ingresar tema
            topic_input = self.driver.find_element(By.ID, "topic-input")
            topic_input.clear()
            topic_input.send_keys("migracion-nube")
            time.sleep(2)
            
            # Paso 3: Analizar tema
            print("Paso 3: Analizando tema para detección de deriva")
            
            analyze_btn = self.driver.find_element(By.ID, "analyze-topic-btn")
            analyze_btn.click()
            
            # Esperar a que se muestre el loading
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.ID, "loading-section"))
            )
            time.sleep(5)  # Simular tiempo de procesamiento
            
            # Paso 4: Mostrar resultados de deriva
            print("Paso 4: Mostrando resultados de análisis de deriva")
            
            # Esperar a que aparezcan los resultados
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.ID, "results-section"))
            )
            time.sleep(3)
            
            # Hacer scroll para ver análisis de deriva
            drift_analysis = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Análisis de Deriva del Tema')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", drift_analysis)
            time.sleep(3)
            
            # Paso 5: Mostrar sugerencias de títulos
            print("Paso 5: Mostrando sugerencias de títulos mejorados")
            
            title_suggestions = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Sugerencias de Títulos Mejorados')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", title_suggestions)
            time.sleep(3)
            
            # Paso 6: Mostrar análisis de palabras clave
            print("Paso 6: Mostrando análisis de palabras clave")
            
            keywords_analysis = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Análisis de Palabras Clave')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", keywords_analysis)
            time.sleep(3)
            
            # Paso 7: Mostrar línea de tiempo
            print("Paso 7: Mostrando línea de tiempo de evolución")
            
            timeline = self.driver.find_element(By.XPATH, "//h3[contains(text(),'Línea de Tiempo de la Conversación')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", timeline)
            time.sleep(3)
            
            # Paso 8: Mostrar configuración
            print("Paso 8: Mostrando panel de configuración")
            
            config_section = self.driver.find_element(By.XPATH, "//h2[contains(text(),'Configuración de Análisis')]")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", config_section)
            time.sleep(3)
            
            # Paso 9: Finalizar demo
            print("Paso 9: Finalizando demostración")
            
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
            ("01_form", "stream-input"),
            ("02_loading", "loading-section"),
            ("03_drift_analysis", "drift-score"),
            ("04_drift_status", "drift-status"),
            ("05_suggestions", "title-suggestions"),
            ("06_keywords", "top-keywords"),
            ("07_timeline", "topic-timeline"),
            ("08_config", "drift-threshold")
        ]
        
        try:
            for name, element_id in screenshots:
                try:
                    element = self.driver.find_element(By.ID, element_id)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
                    time.sleep(1)
                    
                    screenshot_path = f"demo_screenshots/topic_improver_{name}.png"
                    self.driver.save_screenshot(screenshot_path)
                    print(f"Captura guardada: {screenshot_path}")
                    
                except Exception as e:
                    print(f"Error capturando {name}: {e}")
                    
        except Exception as e:
            print(f"Error general en capturas: {e}")
    
    def generate_demo_script(self):
        """Generar script narrado para el video"""
        script_content = """
# Topic Title Improver Demo Script

## Intro (0:00 - 0:15)
"Hola y bienvenidos al demo de Topic Title Improver, una funcionalidad de IA que detecta cuando las conversaciones se desvían del tema original y sugiere títulos mejorados."

## Paso 1: Configuración de Análisis (0:15 - 0:30)
"Primero, ingresamos el canal y el tema que queremos analizar. En este caso, analizaremos el tema 'migracion-nube' en el canal 'development'."

## Paso 2: Procesamiento con IA (0:30 - 1:00)
"Hacemos clic en 'Analizar Tema' y el sistema comienza a procesar la conversación usando algoritmos de NLP y modelos de IA para detectar patrones de deriva."

## Paso 3: Análisis de Deriva (1:00 - 1:45)
"El sistema muestra el análisis de deriva con un puntaje de 0.73, indicando que la conversación se ha desviado significativamente del tema original de migración a la nube."

## Paso 4: Temas Identificados (1:45 - 2:15)
"Podemos ver los temas originales como 'migración' y 'nube', y los nuevos temas que emergieron como 'Kubernetes', 'microservicios' y 'arquitectura'."

## Paso 5: Sugerencias de Títulos (2:15 - 2:45)
"Basado en el análisis, el sistema sugiere títulos mejorados como:
- 'Migración y Arquitectura Cloud'
- 'Cloud Native y Microservicios'
- 'Stack Tecnológico Cloud'

## Paso 6: Análisis de Palabras Clave (2:45 - 3:15)
"El análisis de palabras clave muestra la evolución de la conversación con términos como 'Kubernetes' y 'microservicios' ganando importancia."

## Paso 7: Línea de Tiempo (3:15 - 3:45)
"La línea de tiempo muestra cómo la conversación evolucionó desde el tema original hasta los nuevos temas, permitiendo entender el flujo de la discusión."

## Paso 8: Configuración (3:45 - 4:15)
"Los usuarios pueden ajustar el umbral de deriva, el número mínimo de mensajes para análisis, y la ventana de tiempo."

## Conclusión (4:15 - 4:30)
"Topic Title Improver ayuda a mantener las conversaciones organizadas y facilita encontrar información relevante mediante títulos descriptivos y actualizados."

## Características Técnicas
- Backend Flask con análisis NLP
- Algoritmos de detección de drifting discussions
- Integración con Gemini Pro y Ollama
- Visualización interactiva con Chart.js
- Configuración personalizable de análisis
"""
        
        with open("demo_scripts/topic_improver_script.txt", "w") as f:
            f.write(script_content)
        
        print("Script narrado guardado en demo_scripts/topic_improver_script.txt")
    
    def cleanup(self):
        """Limpiar recursos"""
        if self.driver:
            self.driver.quit()
    
    def run_demo(self):
        """Ejecutar el demo completo"""
        try:
            print("=== Topic Title Improver Demo ===")
            
            # Verificar backend
            if not self.start_backend():
                return
            
            # Generar datos de prueba
            test_data = self.generate_test_topic_data()
            
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
            print("- Script: demo_scripts/topic_improver_script.txt")
            
        except Exception as e:
            print(f"Error en el demo: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    demo = TopicImproverDemo()
    demo.run_demo()
