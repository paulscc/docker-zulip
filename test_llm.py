#!/usr/bin/env python3
"""
Script de prueba para el LLM local (Ollama)
"""

import requests
import json
import sys

def test_ollama_connection(model="gemma2:2b"):
    """
    Prueba la conexión con Ollama y el modelo especificado
    """
    url = "http://localhost:11434/api/generate"
    
    # Datos para la prueba
    data = {
        "model": model,
        "prompt": "Hola, responde brevemente: ¿qué eres?",
        "stream": False
    }
    
    try:
        print(f"🔍 Probando conexión con Ollama usando el modelo: {model}")
        response = requests.post(url, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Conexión exitosa!")
            print(f"📝 Respuesta del modelo: {result.get('response', 'Sin respuesta')}")
            return True
        else:
            print(f"❌ Error en la conexión: {response.status_code}")
            print(f"📄 Detalles: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error al decodificar JSON: {e}")
        return False

def test_multiple_models():
    """
    Prueba múltiples modelos disponibles
    """
    url = "http://localhost:11434/api/tags"
    
    try:
        print("🔍 Obteniendo lista de modelos disponibles...")
        response = requests.get(url)
        
        if response.status_code == 200:
            models = response.json()
            print("📋 Modelos disponibles:")
            for model in models.get('models', []):
                model_name = model.get('name', 'Desconocido')
                print(f"  - {model_name}")
                
                # Probar cada modelo
                if test_ollama_connection(model_name):
                    print(f"✅ {model_name} funciona correctamente")
                else:
                    print(f"❌ {model_name} no funciona")
                print("-" * 50)
        else:
            print(f"❌ Error al obtener modelos: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def interactive_test():
    """
    Modo interactivo para probar el LLM
    """
    print("🤖 Modo interactivo - Escribe 'salir' para terminar")
    print("=" * 50)
    
    while True:
        prompt = input("\n👤 Tú: ")
        if prompt.lower() in ['salir', 'exit', 'quit']:
            break
            
        url = "http://localhost:11434/api/generate"
        data = {
            "model": "gemma2:2b",
            "prompt": prompt,
            "stream": False
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"🤖 IA: {result.get('response', 'Sin respuesta')}")
            else:
                print(f"❌ Error: {response.status_code}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Iniciando pruebas de LLM local")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "interactive":
            interactive_test()
        elif sys.argv[1] == "models":
            test_multiple_models()
        else:
            model = sys.argv[1]
            test_ollama_connection(model)
    else:
        # Prueba básica
        test_ollama_connection()
        
        # Preguntar si quiere modo interactivo
        response = input("\n¿Quieres probar el modo interactivo? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            interactive_test()
