#!/usr/bin/env python3
"""
Script para actualizar bot_config.json con los 8 nuevos bots
"""

import json
import random

def update_bots_config():
    """
    Actualizar configuración con los 8 nuevos bots
    """
    
    # Lista de nuevos bots con sus configuraciones
    new_bots = [
        {
            "bot_name": "nnnnn-bot",
            "email": "nnnnn-bot@midt.127.0.0.1.nip.io",
            "api_key": "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": [
                {"stream": "general", "topic": "chat"},
                {"stream": "noticias", "topic": "general"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 0  # Iniciar inmediatamente
        },
        {
            "bot_name": "aaaaa-bot",
            "email": "aaaaa-bot@midt.127.0.0.1.nip.io",
            "api_key": "Kn3vSm1mJiUKEIoDZQ1IGtaCJDspkbXX",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "casual",
            "channels": [
                {"stream": "general", "topic": "chat"},
                {"stream": "proyectos", "topic": "entretenimiento"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 1  # Iniciar después de 1 segundo
        },
        {
            "bot_name": "tt-bot",
            "email": "tt-bot@midt.127.0.0.1.nip.io",
            "api_key": "HwVy87Cag8cd9sXgNln0D8VuLmrICyog",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "technical",
            "channels": [
                {"stream": "desarrollo", "topic": "general"},
                {"stream": "proyectos", "topic": "updates"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 2  # Iniciar después de 2 segundos
        },
        {
            "bot_name": "yy-bot",
            "email": "yy-bot@midt.127.0.0.1.nip.io",
            "api_key": "AMSLtR84HEG9XeWD820xGsI9W49emFag",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": [
                {"stream": "noticias", "topic": "motivacion"},
                {"stream": "general", "topic": "chat"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 3  # Iniciar después de 3 segundos
        },
        {
            "bot_name": "uu-bot",
            "email": "uu-bot@midt.127.0.0.1.nip.io",
            "api_key": "5SsIvvAbUDPqkd9O3V8kG0UICZLm5jH7",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "professional",
            "channels": [
                {"stream": "desarrollo", "topic": "investigacion"},
                {"stream": "proyectos", "topic": "metrics"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 4  # Iniciar después de 4 segundos
        },
        {
            "bot_name": "ii-bot",
            "email": "ii-bot@midt.127.0.0.1.nip.io",
            "api_key": "VZXtdmZ66e0alod7SdO9sh31jvtRVblS",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "casual",
            "channels": [
                {"stream": "noticias", "topic": "ideas"},
                {"stream": "proyectos", "topic": "innovacion"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 5  # Iniciar después de 5 segundos
        },
        {
            "bot_name": "yyyyy-bot",
            "email": "yyyyy-bot@midt.127.0.0.1.nip.io",
            "api_key": "X6r9KIOZMEcaACvFDmeiRDqMuPswmZby",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "friendly",
            "channels": [
                {"stream": "general", "topic": "chat"},
                {"stream": "proyectos", "topic": "colaboracion"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 6  # Iniciar después de 6 segundos
        },
        {
            "bot_name": "ffff-bot",
            "email": "ffff-bot@midt.127.0.0.1.nip.io",
            "api_key": "XDsjiG1rUAKO3ZR9nsyNvCODlRWnjpQb",
            "server_url": "https://midt.127.0.0.1.nip.io",
            "personality": "technical",
            "channels": [
                {"stream": "desarrollo", "topic": "soluciones"},
                {"stream": "noticias", "topic": "conexion"}
            ],
            "message_interval": 8,
            "use_ollama": True,
            "ollama_url": "http://localhost:11434",
            "ollama_model": "gemma3:1b",
            "random_start_delay": False,
            "start_delay": 7  # Iniciar después de 7 segundos
        }
    ]
    
    try:
        # Leer configuración existente
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Eliminar bots existentes con los mismos emails
        existing_emails = [bot['email'] for bot in new_bots]
        config['bots'] = [bot for bot in config['bots'] if bot.get('email') not in existing_emails]
        
        # Añadir nuevos bots
        config['bots'].extend(new_bots)
        
        # Guardar configuración
        with open('bot_config.json', 'w') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Configuración actualizada con {len(new_bots)} bots")
        print("📋 Bots configurados:")
        for bot in new_bots:
            print(f"  - {bot['bot_name']}: {bot['email']} (delay: {bot['start_delay']}s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error al actualizar configuración: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Actualizando configuración de bots")
    print("=" * 50)
    
    if update_bots_config():
        print("\n✅ Configuración guardada exitosamente")
    else:
        print("\n❌ Error al actualizar configuración")
