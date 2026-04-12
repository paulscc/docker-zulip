#!/usr/bin/env python3
"""
Prueba usando el cliente Zulip directamente
"""

import json
from zulip import Client

# Configuración del bot
bot_config = {
    "email": "ccccc-bot@midt.127.0.0.1.nip.io",
    "api_key": "1bUYflu2kzmG4OuzCg8DtyWRJS5r5fAN",
    "site": "https://midt.127.0.0.1.nip.io"
}

print("🤖 Probando con cliente Zulip directo...")
print("=" * 50)

try:
    # Crear cliente
    client = Client(**bot_config)
    print("✅ Cliente Zulip creado exitosamente")
    
    # Obtener información del usuario
    user_info = client.get_profile()
    print(f"👤 Bot: {user_info.get('full_name', 'Unknown')}")
    print(f"📧 Email: {user_info.get('email', 'Unknown')}")
    
    # Enviar mensaje
    message_data = {
        "type": "stream",
        "to": "general",
        "subject": "chat",
        "content": "Hola desde bot_amigable usando cliente Zulip directo"
    }
    
    print(f"\n📝 Enviando mensaje: {message_data}")
    
    result = client.send_message(message_data)
    print(f"📊 Result: {result}")
    
    if result.get('result') == 'success':
        print(f"✅ Mensaje enviado! ID: {result.get('id')}")
    else:
        print(f"❌ Error: {result.get('msg', 'Unknown error')}")
        
except Exception as e:
    print(f"❌ Excepción: {e}")
    import traceback
    traceback.print_exc()
