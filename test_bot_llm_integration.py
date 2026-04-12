#!/usr/bin/env python3
"""
Script de prueba para la integración entre bots de Zulip y LLM local (Ollama)
"""

import json
import requests
import sys
import time
from typing import Dict, Any

def test_ollama_connection(model="gemma2:2b"):
    """Prueba la conexión con Ollama"""
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": "Responde brevemente: ¿qué puedes hacer en un chat?",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Ollama funciona correctamente")
            print(f"📝 Respuesta: {result.get('response', 'Sin respuesta')}")
            return True
        else:
            print(f"❌ Error en Ollama: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión con Ollama: {e}")
        return False

def test_bot_config():
    """Prueba la configuración de los bots"""
    try:
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        bots = config.get('bots', [])
        print(f"📋 Se encontraron {len(bots)} bots configurados")
        
        for bot in bots:
            name = bot.get('bot_name', 'Sin nombre')
            model = bot.get('ollama_model', 'No configurado')
            use_ollama = bot.get('use_ollama', False)
            personality = bot.get('personality', 'No definida')
            
            print(f"\n🤖 Bot: {name}")
            print(f"   - Personalidad: {personality}")
            print(f"   - Usa Ollama: {use_ollama}")
            print(f"   - Modelo: {model}")
            print(f"   - Canales: {len(bot.get('channels', []))}")
        
        return True
    except Exception as e:
        print(f"❌ Error al leer configuración: {e}")
        return False

def test_llm_message_generation():
    """Prueba la generación de mensajes con diferentes personalidades"""
    personalities = {
        'friendly': 'Saluda amigablemente a alguien nuevo en el chat',
        'technical': 'Explica qué es una API en términos simples',
        'casual': 'Recomienda una buena película para ver',
        'professional': 'Da consejos para mejorar la productividad'
    }
    
    url = "http://localhost:11434/api/generate"
    
    print("\n🧠 Probando generación de mensajes por personalidad:")
    print("=" * 60)
    
    for personality, prompt in personalities.items():
        data = {
            "model": "gemma2:2b",
            "prompt": f"Como un asistente con personalidad {personality}, responde: {prompt}",
            "stream": False
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            if response.status_code == 200:
                result = response.json()
                print(f"\n🎭 {personality.upper()}:")
                print(f"💬 {result.get('response', 'Sin respuesta')}")
            else:
                print(f"❌ Error con personalidad {personality}")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_zulip_server():
    """Prueba si el servidor Zulip está accesible"""
    try:
        response = requests.get("http://localhost:9991", timeout=10)
        if response.status_code == 200:
            print("✅ Servidor Zulip accesible en http://localhost:9991")
            return True
        else:
            print(f"⚠️ Servidor Zulip responde con código {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ No se puede conectar al servidor Zulip: {e}")
        return False

def interactive_bot_test():
    """Prueba interactiva de un bot con LLM"""
    print("\n🤖 Modo interactivo - Simulación de bot")
    print("=" * 50)
    print("Escribe 'salir' para terminar")
    
    bot_personalities = ['friendly', 'technical', 'casual', 'professional']
    
    while True:
        print("\nPersonalidades disponibles:")
        for i, personality in enumerate(bot_personalities, 1):
            print(f"{i}. {personality}")
        
        try:
            choice = input("\nElige una personalidad (1-4) o 'salir': ")
            if choice.lower() in ['salir', 'exit', 'quit']:
                break
            
            choice_idx = int(choice) - 1
            if 0 <= choice_idx < len(bot_personalities):
                personality = bot_personalities[choice_idx]
                user_message = input("👤 Usuario: ")
                
                # Generar respuesta del bot
                url = "http://localhost:11434/api/generate"
                prompt = f"Como un bot con personalidad {personality}, responde a este mensaje de forma natural y concisa: '{user_message}'"
                
                data = {
                    "model": "gemma2:2b",
                    "prompt": prompt,
                    "stream": False
                }
                
                response = requests.post(url, json=data, timeout=30)
                if response.status_code == 200:
                    result = response.json()
                    print(f"🤖 Bot ({personality}): {result.get('response', 'Sin respuesta')}")
                else:
                    print("❌ Error al generar respuesta")
            else:
                print("❌ Opción inválida")
        except ValueError:
            print("❌ Ingresa un número válido")
        except KeyboardInterrupt:
            break

def main():
    print("🚀 Iniciando pruebas de integración Bot-Zulip-LLM")
    print("=" * 60)
    
    # Pruebas básicas
    tests = [
        ("Conexión con Ollama", test_ollama_connection),
        ("Configuración de Bots", test_bot_config),
        ("Servidor Zulip", test_zulip_server),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n🔍 Probando: {test_name}")
        print("-" * 40)
        result = test_func()
        results.append((test_name, result))
        time.sleep(1)
    
    # Resumen de pruebas
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name}: {status}")
    
    # Prueba de generación de mensajes
    if any(result for _, result in results):
        print("\n🧠 Probando generación de mensajes con LLM...")
        test_llm_message_generation()
        
        # Modo interactivo
        response = input("\n¿Quieres probar el modo interactivo? (s/n): ")
        if response.lower() in ['s', 'si', 'y', 'yes']:
            interactive_bot_test()
    
    print("\n🎉 Pruebas completadas!")

if __name__ == "__main__":
    main()
