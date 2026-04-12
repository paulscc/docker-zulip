#!/usr/bin/env python3
"""
Script para iniciar los 8 nuevos bots con form data
"""

import json
import requests
import time
import threading
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import base64

# Deshabilitar advertencias SSL
urllib3.disable_warnings(InsecureRequestWarning)

class SimpleBot:
    def __init__(self, config):
        self.config = config
        self.email = config['email']
        self.api_key = config['api_key']
        self.site = config['server_url']
        self.bot_name = config['bot_name']
        self.personality = config.get('personality', 'friendly')
        self.channels = config.get('channels', [])
        self.message_interval = config.get('message_interval', 8)
        self.use_ollama = config.get('use_ollama', True)
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.ollama_model = config.get('ollama_model', 'gemma3:1b')
        self.start_delay = config.get('start_delay', 0)
        self.running = False
        
        # Crear headers de autenticación
        auth_string = f"{self.email}:{self.api_key}"
        auth_bytes = auth_string.encode('ascii')
        self.auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {self.auth_b64}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        self.base_url = f"{self.site}/api/v1"
    
    def generate_message(self, context=None):
        """Generar mensaje usando Ollama"""
        if not self.use_ollama:
            return f"Mensaje desde {self.bot_name}"
        
        try:
            personality_prompts = {
                'friendly': "Eres un bot amigable y sociable. Responde de manera casual y positiva.",
                'technical': "Eres un bot técnico especializado en desarrollo y sistemas. Responde con términos técnicos pero claros.",
                'casual': "Eres un bot informal y relajado. Responde de manera casual y entretenida.",
                'professional': "Eres un bot profesional y formal. Responde de manera educada y corporativa."
            }
            
            prompt = personality_prompts.get(self.personality, "Eres un bot amigable.")
            
            if context and 'channel' in context:
                prompt += f"\nEstás escribiendo en el canal #{context['channel']}."
            
            prompt += "\nGenera un mensaje breve y natural para la conversación actual:"
            
            payload = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 50
                }
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=5)
            if response.status_code == 200:
                result = response.json()
                return result.get('response', f"Mensaje desde {self.bot_name}").strip()
            else:
                return f"Mensaje desde {self.bot_name}"
                
        except Exception as e:
            print(f"Ollama error for {self.bot_name}: {e}")
            return f"Mensaje desde {self.bot_name}"
    
    def send_message(self, stream, topic, content):
        """Enviar mensaje usando form data"""
        try:
            # Obtener stream ID
            response = requests.get(f"{self.base_url}/streams", headers={'Authorization': f'Basic {self.auth_b64}'}, verify=False, timeout=5)
            
            if response.status_code == 200:
                streams = response.json()
                stream_id = None
                for s in streams.get('streams', []):
                    if s.get('name', '').lower() == stream.lower():
                        stream_id = s.get('stream_id')
                        break
                
                if stream_id:
                    form_data = {
                        'type': 'stream',
                        'to': str(stream_id),
                        'topic': topic,
                        'content': content
                    }
                    
                    response = requests.post(f"{self.base_url}/messages", data=form_data, headers=self.headers, verify=False, timeout=5)
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"[{self.bot_name}] Message sent to {stream}/{topic} (ID: {result.get('id')})")
                        return True
                    else:
                        print(f"[{self.bot_name}] Error sending message: {response.status_code}")
                        return False
                else:
                    print(f"[{self.bot_name}] Stream '{stream}' not found")
                    return False
            else:
                print(f"[{self.bot_name}] Error getting streams: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"[{self.bot_name}] Error: {e}")
            return False
    
    def start_conversation(self):
        """Iniciar conversación automatizada"""
        self.running = True
        
        def conversation_loop():
            # Esperar el delay de inicio
            if self.start_delay > 0:
                print(f"[{self.bot_name}] Starting in {self.start_delay} seconds...")
                time.sleep(self.start_delay)
            
            while self.running:
                for channel in self.channels:
                    if not self.running:
                        break
                    
                    stream = channel['stream']
                    topic = channel.get('topic', 'general')
                    context = {'channel': stream}
                    message = self.generate_message(context)
                    
                    success = self.send_message(stream, topic, f"@**{self.bot_name}**: {message}")
                    
                    if not success:
                        print(f"[{self.bot_name}] Failed to send message to {stream}/{topic}")
                
                # Esperar entre mensajes
                time.sleep(self.message_interval)
        
        # Iniciar hilo de conversación
        self.conversation_thread = threading.Thread(target=conversation_loop)
        self.conversation_thread.daemon = True
        self.conversation_thread.start()
        print(f"[{self.bot_name}] Conversation started")
    
    def stop_conversation(self):
        """Detener conversación"""
        self.running = False
        print(f"[{self.bot_name}] Conversation stopped")

def start_all_new_bots():
    """Iniciar todos los bots nuevos"""
    print("Starting all new bots...")
    print("=" * 50)
    
    try:
        # Leer configuración
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Obtener solo los 8 bots nuevos
        new_bot_names = ['nnnnn-bot', 'aaaaa-bot', 'tt-bot', 'yy-bot', 'uu-bot', 'ii-bot', 'yyyyy-bot', 'ffff-bot']
        new_bots = [bot for bot in config['bots'] if bot['bot_name'] in new_bot_names]
        
        bots = []
        for bot_config in new_bots:
            bot = SimpleBot(bot_config)
            bots.append(bot)
            bot.start_conversation()
            time.sleep(0.1)  # Pequeña pausa entre inicios
        
        print(f"\n{len(bots)} bots started successfully!")
        print("Bots are now sending messages every 8 seconds with different start delays.")
        
        # Mantener el script corriendo
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping all bots...")
            for bot in bots:
                bot.stop_conversation()
            print("All bots stopped.")
        
    except Exception as e:
        print(f"Error starting bots: {e}")

if __name__ == "__main__":
    start_all_new_bots()
