#!/usr/bin/env python3
"""
Setup script for creating Zulip bots
This script helps you create multiple bots in your Zulip server
"""

import subprocess
import json
import sys
from zulip_bots_framework import ZulipBotManager

def check_docker_zulip_running():
    """Check if Zulip Docker container is running"""
    try:
        result = subprocess.run(['docker', 'compose', 'ps'], 
                              capture_output=True, text=True, cwd='.')
        if 'zulip' in result.stdout and 'Up' in result.stdout:
            return True
        return False
    except Exception:
        return False

def create_bot_instructions():
    """Print instructions for creating bots in Zulip"""
    print("""
=== INSTRUCCIONES PARA CREAR BOTS EN ZULIP ===

1. Accede a tu servidor Zulip en http://localhost:9991

2. Inicia sesión como administrador

3. Para crear cada bot:
   - Ve a "Settings" (engranaje) > "Add bots and integrations"
   - Click en "Add a new bot"
   - Tipo: "Generic bot"
   - Bot name: Usa los nombres del archivo bot_config.json
   - Bot email: Usa los emails del archivo bot_config.json
   - Click en "Create bot"

4. Después de crear cada bot:
   - Descarga el archivo .zuliprc del bot
   - Copia el API key del archivo .zuliprc
   - Actualiza el API key en bot_config.json

5. Crea los canales necesarios:
   - general
   - social  
   - tecnico
   - desarrollo
   - random
   - proyectos
   - anuncios

=== COMANDOS PARA EJECUTAR LOS BOTS ===

# Instalar dependencias:
pip install -r requirements.txt

# Listar bots configurados:
python zulip_bots_framework.py --action list

# Iniciar todos los bots:
python zulip_bots_framework.py --action start-all

# Iniciar un bot específico:
python zulip_bots_framework.py --action start --bot bot_amigable

# Detener todos los bots:
python zulip_bots_framework.py --action stop-all

# Enviar mensaje manual desde un bot:
python zulip_bots_framework.py --action message --bot bot_amigable --stream general --topic chat --message "Hola mundo!"

""")

def main():
    print("=== ZULIP MULTI-BOT SETUP ===")
    
    # Check if Zulip is running
    if not check_docker_zulip_running():
        print("ADVERTENCIA: No se detectó que Zulip esté corriendo.")
        print("Asegúrate de iniciar Zulip con: docker compose up -d")
        print("Luego accede a http://localhost:9991")
    else:
        print("Zulip Docker detectado corriendo correctamente.")
    
    # Create bot configuration if needed
    manager = ZulipBotManager('bot_config.json')
    
    # Show instructions
    create_bot_instructions()
    
    # Test framework
    print("\n=== VERIFICANDO CONFIGURACIÓN ===")
    manager.list_bots()

if __name__ == '__main__':
    main()
