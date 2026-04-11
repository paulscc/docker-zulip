#!/usr/bin/env python3
"""
Zulip Multi-Bot Framework
A framework for creating and managing multiple Zulip chat bots
"""

import json
import time
import random
import threading
import requests
from typing import Dict, List, Any
from zulip import Client

class ZulipBot:
    """Base class for Zulip bots"""
    
    def __init__(self, config: Dict[str, Any], initialize_client: bool = False):
        self.config = config
        self.email = config['email']
        self.api_key = config['api_key']
        self.server_url = config['server_url']
        self.bot_name = config['bot_name']
        self.personality = config.get('personality', 'friendly')
        self.channels = config.get('channels', [])
        self.use_ollama = config.get('use_ollama', True)
        self.ollama_url = config.get('ollama_url', 'http://localhost:11434')
        self.ollama_model = config.get('ollama_model', 'llama3')
        self.random_start_delay = config.get('random_start_delay', True)
        
        # Initialize Zulip client only when needed
        self.client = None
        if initialize_client:
            self._init_client()
        
        self.running = False
        self.message_queue = []
    
    def _init_client(self):
        """Initialize Zulip client"""
        if self.client is None:
            self.client = Client(
                email=self.email,
                api_key=self.api_key,
                site=self.server_url
            )
        
    def usage(self) -> str:
        """Return bot usage description"""
        channel_names = [ch.get('stream', 'unknown') for ch in self.channels]
        return f"Bot: {self.bot_name}\nPersonality: {self.personality}\nChannels: {', '.join(channel_names)}"
    
    def generate_message(self, context: Dict[str, Any] = None) -> str:
        """Generate a message based on bot personality and context"""
        if self.use_ollama:
            return self._generate_ollama_message(context)
        else:
            return self._generate_predefined_message(context)
    
    def _generate_ollama_message(self, context: Dict[str, Any] = None) -> str:
        """Generate message using Ollama3 AI"""
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
                return result.get('response', self._generate_predefined_message(context)).strip()
            else:
                return self._generate_predefined_message(context)
                
        except Exception as e:
            print(f"Ollama error for {self.bot_name}: {e}")
            return self._generate_predefined_message(context)
    
    def _generate_predefined_message(self, context: Dict[str, Any] = None) -> str:
        """Generate predefined message based on personality"""
        messages = {
            'friendly': [
                "¡Hola a todos! ¿Cómo están?",
                "Buen día equipo!",
                "Es un placer estar aquí con ustedes.",
                "¿Alguien quiere conversar?",
                "Qué buen ambiente en este canal!"
            ],
            'technical': [
                "Revisando los logs del sistema...",
                "¿Alguien necesita ayuda técnica?",
                "Optimizando procesos actuales.",
                "Monitorizando el rendimiento.",
                "Actualización de componentes completada."
            ],
            'casual': [
                "¿Qué hay de nuevo?",
                "Alguien vio el partido de ayer?",
                "Café time!",
                "Fin de semana cerca!",
                "Compartiendo algo interesante..."
            ],
            'professional': [
                "Buenos días, equipo.",
                "Actualización sobre el proyecto.",
                "Recordatorio de la reunión de hoy.",
                "Informes disponibles para revisión.",
                "Manteniendo la productividad."
            ]
        }
        
        personality_messages = messages.get(self.personality, messages['friendly'])
        return random.choice(personality_messages)
    
    def send_message(self, stream: str, topic: str, content: str) -> bool:
        """Send a message to a Zulip stream"""
        try:
            if self.client is None:
                self._init_client()
            result = self.client.send_message({
                'type': 'stream',
                'to': stream,
                'topic': topic,
                'content': content
            })
            return result['result'] == 'success'
        except Exception as e:
            print(f"Error sending message from {self.bot_name}: {e}")
            return False
    
    def send_private_message(self, user_email: str, content: str) -> bool:
        """Send a private message to a user"""
        try:
            if self.client is None:
                self._init_client()
            result = self.client.send_message({
                'type': 'private',
                'to': user_email,
                'content': content
            })
            return result['result'] == 'success'
        except Exception as e:
            print(f"Error sending private message from {self.bot_name}: {e}")
            return False
    
    def start_conversation(self):
        """Start automated conversations in configured channels"""
        self.running = True
        
        def conversation_loop():
            # Random start delay
            if self.random_start_delay:
                start_delay = random.randint(1, 10)
                print(f"[{self.bot_name}] Starting in {start_delay} seconds...")
                time.sleep(start_delay)
            
            while self.running:
                for channel in self.channels:
                    if not self.running:
                        break
                    
                    stream = channel['stream']
                    topic = channel.get('topic', 'general')
                    context = {'channel': stream}
                    message = self.generate_message(context)
                    
                    success = self.send_message(stream, topic, f"@**{self.bot_name}**: {message}")
                    if success:
                        print(f"[{self.bot_name}] Message sent to {stream}/{topic}")
                    else:
                        print(f"[{self.bot_name}] Failed to send message to {stream}/{topic}")
                
                # Wait between messages with random variation
                base_interval = self.config.get('message_interval', 8)
                random_variation = random.randint(-2, 3)  # +/- 2 seconds variation
                actual_interval = max(3, base_interval + random_variation)  # Minimum 3 seconds
                time.sleep(actual_interval)
        
        # Start conversation thread
        self.conversation_thread = threading.Thread(target=conversation_loop)
        self.conversation_thread.daemon = True
        self.conversation_thread.start()
        print(f"[{self.bot_name}] Conversation started")
    
    def stop_conversation(self):
        """Stop automated conversations"""
        self.running = False
        if hasattr(self, 'conversation_thread'):
            self.conversation_thread.join(timeout=5)
        print(f"[{self.bot_name}] Conversation stopped")

class ZulipBotManager:
    """Manager for multiple Zulip bots"""
    
    def __init__(self, config_file: str):
        self.config_file = config_file
        self.bots = {}
        self.load_configuration()
    
    def load_configuration(self):
        """Load bot configurations from file"""
        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
            for bot_config in config.get('bots', []):
                bot = ZulipBot(bot_config)
                self.bots[bot.bot_name] = bot
                
            print(f"Loaded {len(self.bots)} bot configurations")
        except FileNotFoundError:
            print(f"Configuration file {self.config_file} not found")
            self.create_sample_config()
        except json.JSONDecodeError as e:
            print(f"Error parsing configuration file: {e}")
    
    def create_sample_config(self):
        """Create a sample configuration file"""
        sample_config = {
            "bots": [
                {
                    "bot_name": "bot_amigable",
                    "email": "bot_amigable@example.com",
                    "api_key": "YOUR_API_KEY_HERE",
                    "server_url": "http://localhost:9991",
                    "personality": "friendly",
                    "channels": [
                        {"stream": "general", "topic": "chat"},
                        {"stream": "social", "topic": "conversacion"}
                    ],
                    "message_interval": 300
                },
                {
                    "bot_name": "bot_tecnico",
                    "email": "bot_tecnico@example.com", 
                    "api_key": "YOUR_API_KEY_HERE",
                    "server_url": "http://localhost:9991",
                    "personality": "technical",
                    "channels": [
                        {"stream": "tecnico", "topic": "soporte"},
                        {"stream": "desarrollo", "topic": "updates"}
                    ],
                    "message_interval": 400
                },
                {
                    "bot_name": "bot_casual",
                    "email": "bot_casual@example.com",
                    "api_key": "YOUR_API_KEY_HERE", 
                    "server_url": "http://localhost:9991",
                    "personality": "casual",
                    "channels": [
                        {"stream": "random", "topic": "off-topic"},
                        {"stream": "social", "topic": "entretenimiento"}
                    ],
                    "message_interval": 350
                }
            ]
        }
        
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        print(f"Sample configuration created at {self.config_file}")
        print("Please edit the configuration file with your actual bot credentials")
    
    def start_bot(self, bot_name: str) -> bool:
        """Start a specific bot"""
        if bot_name not in self.bots:
            print(f"Bot {bot_name} not found")
            return False
        
        bot = self.bots[bot_name]
        bot.start_conversation()
        return True
    
    def stop_bot(self, bot_name: str) -> bool:
        """Stop a specific bot"""
        if bot_name not in self.bots:
            print(f"Bot {bot_name} not found")
            return False
        
        bot = self.bots[bot_name]
        bot.stop_conversation()
        return True
    
    def start_all_bots(self):
        """Start all configured bots"""
        print("Starting all bots...")
        for bot_name in self.bots:
            self.start_bot(bot_name)
    
    def stop_all_bots(self):
        """Stop all running bots"""
        print("Stopping all bots...")
        for bot_name in self.bots:
            self.stop_bot(bot_name)
    
    def list_bots(self):
        """List all configured bots"""
        print("\n=== Configured Bots ===")
        for bot_name, bot in self.bots.items():
            status = "Running" if bot.running else "Stopped"
            print(f"- {bot_name}: {status}")
            print(f"  Personality: {bot.personality}")
            print(f"  Channels: {len(bot.channels)}")
            print(f"  Usage: {bot.usage()}")
            print()
    
    def send_message_from_bot(self, bot_name: str, stream: str, topic: str, message: str) -> bool:
        """Send a specific message from a bot"""
        if bot_name not in self.bots:
            print(f"Bot {bot_name} not found")
            return False
        
        bot = self.bots[bot_name]
        return bot.send_message(stream, topic, message)

def main():
    """Main function for running the bot manager"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Zulip Multi-Bot Manager')
    parser.add_argument('--config', default='bot_config.json', help='Configuration file path')
    parser.add_argument('--action', choices=['start', 'stop', 'list', 'start-all', 'stop-all', 'message'], 
                       required=True, help='Action to perform')
    parser.add_argument('--bot', help='Bot name (for start/stop/message actions)')
    parser.add_argument('--stream', help='Stream name (for message action)')
    parser.add_argument('--topic', help='Topic name (for message action)')
    parser.add_argument('--message', help='Message content (for message action)')
    
    args = parser.parse_args()
    
    manager = ZulipBotManager(args.config)
    
    if args.action == 'list':
        manager.list_bots()
    elif args.action == 'start-all':
        manager.start_all_bots()
    elif args.action == 'stop-all':
        manager.stop_all_bots()
    elif args.action == 'start':
        if not args.bot:
            print("Bot name required for start action")
            return
        manager.start_bot(args.bot)
    elif args.action == 'stop':
        if not args.bot:
            print("Bot name required for stop action")
            return
        manager.stop_bot(args.bot)
    elif args.action == 'message':
        if not all([args.bot, args.stream, args.topic, args.message]):
            print("Bot name, stream, topic, and message required for message action")
            return
        success = manager.send_message_from_bot(args.bot, args.stream, args.topic, args.message)
        print(f"Message {'sent' if success else 'failed to send'}")

if __name__ == '__main__':
    main()
