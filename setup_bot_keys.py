#!/usr/bin/env python3
"""
Script automático para configurar los bots de Zulip
Crea las API keys y configura el archivo .env automáticamente
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def create_env_file():
    """Crea el archivo .env a partir de .env.example"""
    
    # Verificar si .env.example existe
    env_example_path = Path(".env.example")
    if not env_example_path.exists():
        print("Error: No se encuentra el archivo .env.example")
        return False
    
    # Leer el archivo example
    with open(env_example_path, 'r', encoding='utf-8') as f:
        env_content = f.read()
    
    # Crear .env
    env_path = Path(".env")
    if env_path.exists():
        overwrite = input("El archivo .env ya existe. ¿Deseas sobrescribirlo? (y/n): ")
        if overwrite.lower() != 'y':
            print("Operación cancelada.")
            return False
    
    # Configuración interactiva
    print("=== Configuración Automática de Bots Zulip ===")
    print("Por favor, ingresa la siguiente información:")
    print()
    
    # Configuración del servidor Zulip
    zulip_server = input("Servidor Zulip (ej: https://tu-servidor.zulipchat.com): ").strip()
    
    # Configurar cada bot
    bots_config = {
        'SUMMARY_BOT': {
            'email': input("Email del bot de resúmenes (ej: summary-bot@tu-servidor.zulipchat.com): ").strip(),
            'api_key': input("API key del bot de resúmenes: ").strip()
        },
        'TOPIC_ANALYZER_BOT': {
            'email': input("Email del bot de análisis de tópicos (ej: topic-analyzer-bot@tu-servidor.zulipchat.com): ").strip(),
            'api_key': input("API key del bot de análisis de tópicos: ").strip()
        },
        'FOCUS_BOT': {
            'email': input("Email del bot de monitoreo de enfoque (ej: focus-monitor-bot@tu-servidor.zulipchat.com): ").strip(),
            'api_key': input("API key del bot de monitoreo de enfoque: ").strip()
        },
        'WEBHOOK_BOT': {
            'email': input("Email del bot de webhook (ej: webhook-bot@tu-servidor.zulipchat.com): ").strip(),
            'api_key': input("API key del bot de webhook: ").strip()
        }
    }
    
    # Configuración de IA
    gemini_api_key = input("API key de Gemini (opcional): ").strip()
    ollama_url = input("URL de Ollama (default: http://localhost:11434): ").strip() or "http://localhost:11434"
    
    # Reemplazar variables en el contenido
    env_content = env_content.replace("https://tu-servidor.zulipchat.com", zulip_server)
    
    for bot_name, config in bots_config.items():
        env_content = env_content.replace(f"{bot_name}_EMAIL=summary-bot@tu-servidor.zulipchat.com", 
                                         f"{bot_name}_EMAIL={config['email']}")
        env_content = env_content.replace(f"{bot_name}_API_KEY=XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX", 
                                         f"{bot_name}_API_KEY={config['api_key']}")
        env_content = env_content.replace(f"{bot_name}_SERVER=https://tu-servidor.zulipchat.com", 
                                         f"{bot_name}_SERVER={zulip_server}")
    
    if gemini_api_key:
        env_content = env_content.replace("tu-gemini-api-key-aqui", gemini_api_key)
    
    env_content = env_content.replace("http://localhost:11434", ollama_url)
    
    # Escribir el archivo .env
    with open(env_path, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"\\n¡Archivo .env creado exitosamente!")
    print(f"Configuración guardada en: {env_path.absolute()}")
    
    return True

def create_bot_instructions():
    """Crea un archivo con instrucciones para crear los bots en Zulip"""
    
    instructions = """
# Instrucciones para Crear Bots en Zulip

## Pasos para crear cada bot:

### 1. Bot de Resúmenes (Summary Bot)
1. Entra a tu servidor Zulip como administrador
2. Ve a Settings -> Bots -> Add a new bot
3. Tipo: Generic bot
4. Bot name: Summary Bot
5. Bot email: summary-bot@tu-servidor.zulipchat.com
6. Bot avatar: (opcional)
7. Crea el bot y copia la API key

### 2. Bot de Análisis de Tópicos (Topic Analyzer Bot)
1. Tipo: Generic bot
2. Bot name: Topic Analyzer Bot
3. Bot email: topic-analyzer-bot@tu-servidor.zulipchat.com
4. Crea el bot y copia la API key

### 3. Bot de Monitoreo de Enfoque (Focus Monitor Bot)
1. Tipo: Generic bot
2. Bot name: Focus Monitor Bot
3. Bot email: focus-monitor-bot@tu-servidor.zulipchat.com
4. Crea el bot y copia la API key

### 4. Bot de Webhook (Webhook Bot)
1. Tipo: Generic bot
2. Bot name: Webhook Bot
3. Bot email: webhook-bot@tu-servidor.zulipchat.com
4. Crea el bot y copia la API key

## Configuración de Permisos:
Asegúrate de que cada bot tenga los permisos necesarios:
- Acceso a los streams relevantes
- Capacidad de leer mensajes
- Capacidad de enviar mensajes
- Acceso a la API de Zulip

## Una vez creados los bots:
Ejecuta: python setup_bot_keys.py
Este script configurará automáticamente tu archivo .env
"""
    
    with open("BOT_CREATION_INSTRUCTIONS.md", 'w', encoding='utf-8') as f:
        f.write(instructions)
    
    print("Instrucciones para crear bots guardadas en: BOT_CREATION_INSTRUCTIONS.md")

def main():
    """Función principal"""
    
    print("=== Configuración de Bots Zulip ===")
    print()
    
    # Crear instrucciones si no existen
    if not Path("BOT_CREATION_INSTRUCTIONS.md").exists():
        create_bot_instructions()
        print()
        print("Primero, sigue las instrucciones en BOT_CREATION_INSTRUCTIONS.md")
        print("para crear los bots en tu servidor Zulip.")
        print()
        input("Presiona Enter cuando hayas creado los bots y tengas las API keys...")
        print()
    
    # Crear archivo .env
    if create_env_file():
        print()
        print("=== Configuración completada ===")
        print("Ahora puedes ejecutar:")
        print("  docker-compose up -d")
        print("  python app.py")
        print()
        print("Los bots utilizarán automáticamente las credenciales configuradas.")
    else:
        print("Error en la configuración. Por favor, revisa los mensajes anteriores.")
        sys.exit(1)

if __name__ == "__main__":
    main()
