#!/usr/bin/env python3
"""
Script para arreglar el problema de mensajes de yyyyy-bot
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

class FixedBot:
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
        """Generar mensaje usando Ollama con mejor manejo de errores"""
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
                    "max_tokens": 30  # Reducir tokens para respuestas más rápidas
                }
            }
            
            # Aumentar timeout y usar retries
            for attempt in range(3):
                try:
                    response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=15)
                    if response.status_code == 200:
                        result = response.json()
                        message = result.get('response', f"Mensaje desde {self.bot_name}").strip()
                        if message and len(message) > 5:
                            return message
                        else:
                            return f"Mensaje desde {self.bot_name}"
                    else:
                        print(f"[{self.bot_name}] Ollama attempt {attempt + 1} failed: {response.status_code}")
                        if attempt < 2:
                            time.sleep(1)
                except requests.exceptions.Timeout:
                    print(f"[{self.bot_name}] Ollama timeout attempt {attempt + 1}")
                    if attempt < 2:
                        time.sleep(1)
                except Exception as e:
                    print(f"[{self.bot_name}] Ollama error attempt {attempt + 1}: {e}")
                    if attempt < 2:
                        time.sleep(1)
            
            # Si todo falla, usar mensaje predefinido
            fallback_messages = {
                'friendly': ["¡Hola a todos! ¿Cómo están?", "¡Buen día! ¿Qué tal todo?", "¡Saludos! Espero que estén bien."],
                'technical': ["Revisando el sistema actual", "Analizando el código", "Optimizando el rendimiento"],
                'casual': ["¿Qué onda?", "¿Cómo va todo?", "¿Alguna novedad?"],
                'professional': ["Buenos días a todos", "Saludos cordiales", "Espero que tengan un buen día"]
            }
            
            import random
            messages = fallback_messages.get(self.personality, ["Mensaje desde el bot"])
            return random.choice(messages)
                
        except Exception as e:
            print(f"[{self.bot_name}] Critical error in message generation: {e}")
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
                        print(f"[{self.bot_name}] Message sent to {stream}/{topic} (ID: {result.get('id')}) - '{content[:30]}...'")
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

def test_yyyyy_bot():
    """Probar específicamente el yyyyy-bot"""
    print("Testing yyyyy-bot with improved message generation...")
    print("=" * 50)
    
    try:
        # Leer configuración
        with open('bot_config.json', 'r') as f:
            config = json.load(f)
        
        # Encontrar yyyyy-bot
        yyyyy_bot_config = None
        for bot in config['bots']:
            if bot['bot_name'] == 'yyyyy-bot':
                yyyyy_bot_config = bot
                break
        
        if not yyyyy_bot_config:
            print("yyyyy-bot not found in configuration")
            return False
        
        # Crear y probar el bot
        bot = FixedBot(yyyyy_bot_config)
        
        # Probar generación de mensajes
        print("Testing message generation...")
        for i in range(3):
            message = bot.generate_message({'channel': 'general'})
            print(f"Message {i+1}: {message}")
            time.sleep(1)
        
        # Probar envío de mensaje
        print("\nTesting message sending...")
        success = bot.send_message('general', 'Test', f"@**yyyyy-bot**: {bot.generate_message({'channel': 'general'})}")
        
        if success:
            print("yyyyy-bot is working correctly!")
            return True
        else:
            print("yyyyy-bot has issues")
            return False
        
    except Exception as e:
        print(f"Error testing yyyyy-bot: {e}")
        return False

if __name__ == "__main__":
    test_yyyyy_bot()
