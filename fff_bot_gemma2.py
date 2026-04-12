#!/usr/bin/env python3
"""
Bot fff-bot con Gemma2
Usa el bot fff-bot para enviar mensajes generados por Gemma2 local
"""

import requests
import json
import time
from datetime import datetime
import urllib3

# Deshabilitar advertencias SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FFFBotGemma2:
    def __init__(self):
        """Inicializar el bot con las credenciales proporcionadas"""
        self.bot_email = "fff-bot@127.0.0.1.nip.io"
        self.api_key = "WwxhtPfHGMySSuDWK1cYBRAzIuUXPLdv"
        self.server_url = "https://127.0.0.1.nip.io"
        self.ollama_url = "http://localhost:11434"
        self.model = "gemma2"
        
        self.headers = {
            "Content-Type": "application/json"
        }
        self.auth = (self.bot_email, self.api_key)
    
    def test_connection(self):
        """Probar conexión con Zulip"""
        try:
            response = requests.get(
                f"{self.server_url}/api/v1/users/me",
                headers=self.headers,
                auth=self.auth,
                verify=False,
                timeout=10
            )
            return response.status_code == 200
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def generate_message_with_gemma2(self, prompt, personality="friendly"):
        """Generar mensaje usando Gemma2 local"""
        try:
            # Personalidad base según el tipo
            personality_prompts = {
                "friendly": "Eres un bot amigable y positivo. Responde de manera alegre y entusiasta.",
                "technical": "Eres un bot técnico y profesional. Responde con información precisa y útil.",
                "casual": "Eres un bot casual y relajado. Responde de manera informal y cercana."
            }
            
            system_prompt = personality_prompts.get(personality, personality_prompts["friendly"])
            
            payload = {
                "model": self.model,
                "prompt": f"{system_prompt}\n\n{prompt}",
                "stream": False
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Lo siento, no pude generar una respuesta.")
            else:
                return f"Error al generar mensaje: {response.status_code}"
                
        except Exception as e:
            return f"Error con Gemma2: {e}"
    
    def send_message(self, stream, topic, content):
        """Enviar mensaje a un canal de Zulip"""
        payload = {
            "type": "stream",
            "to": stream,
            "topic": topic,
            "content": content
        }
        
        try:
            response = requests.post(
                f"{self.server_url}/api/v1/messages",
                headers=self.headers,
                json=payload,
                auth=self.auth,
                verify=False,
                timeout=10
            )
            
            return response.status_code == 200
        except Exception as e:
            print(f"Error al enviar mensaje: {e}")
            return False
    
    def interactive_chat(self):
        """Modo de chat interactivo"""
        print("=== FFF-BOT CON GEMMA2 ===")
        print("Bot configurado para usar Gemma2 local")
        print("Escribe 'salir' para terminar")
        print("Formato: canal:topic mensaje")
        print("Ejemplo: general:hola ¿Cómo están todos?")
        print()
        
        while True:
            try:
                user_input = input("> ").strip()
                
                if user_input.lower() == 'salir':
                    print("¡Adiós!")
                    break
                
                if ':' not in user_input:
                    print("Formato incorrecto. Usa: canal:topic mensaje")
                    continue
                
                parts = user_input.split(':', 2)
                if len(parts) < 3:
                    print("Formato incorrecto. Usa: canal:topic mensaje")
                    continue
                
                stream, topic, message = parts
                
                print(f"Generando respuesta con Gemma2...")
                response = self.generate_message_with_gemma2(message, "friendly")
                
                print(f"Enviando a #{stream} > {topic}...")
                if self.send_message(stream, topic, response):
                    print("¡Mensaje enviado!")
                else:
                    print("Error al enviar mensaje")
                
                print()
                
            except KeyboardInterrupt:
                print("\n¡Adiós!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def auto_messages(self, duration_minutes=5):
        """Enviar mensajes automáticos durante un tiempo"""
        print(f"=== ENVIANDO MENSAJES AUTOMÁTICOS POR {duration_minutes} MINUTOS ===")
        
        streams = ["noticias", "proyectos", "general", "desarrollo"]
        topics = ["general", "chat", "actualizaciones", "alegria"]
        
        prompts = [
            "Comparte algo positivo y motivador",
            "Cuéntame una curiosidad interesante",
            "Dame un consejo útil para el trabajo",
            "Comparte una idea inspiradora",
            "Haz una pregunta reflexiva"
        ]
        
        end_time = time.time() + (duration_minutes * 60)
        message_count = 0
        
        while time.time() < end_time:
            try:
                # Seleccionar aleatoriamente canal, topic y prompt
                stream = streams[message_count % len(streams)]
                topic = topics[message_count % len(topics)]
                prompt = prompts[message_count % len(prompts)]
                
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Generando mensaje para #{stream}...")
                
                response = self.generate_message_with_gemma2(prompt, "friendly")
                
                if self.send_message(stream, topic, response):
                    message_count += 1
                    print(f"Mensaje #{message_count} enviado a #{stream} > {topic}")
                else:
                    print("Error al enviar mensaje")
                
                # Esperar 30 segundos entre mensajes
                time.sleep(30)
                
            except KeyboardInterrupt:
                print("\nDeteniendo envío automático...")
                break
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)
        
        print(f"\nTotal de mensajes enviados: {message_count}")

def main():
    """Función principal"""
    bot = FFFBotGemma2()
    
    print("=== FFF-BOT CON GEMMA2 ===")
    print("Verificando conexión...")
    
    if not bot.test_connection():
        print("Error: No se puede conectar con Zulip")
        print("Verifica que el servidor esté funcionando y las credenciales sean correctas")
        return
    
    print("Conexión exitosa!")
    
    print("\n¿Qué quieres hacer?")
    print("1. Chat interactivo")
    print("2. Enviar mensajes automáticos (5 minutos)")
    print("3. Enviar mensajes automáticos (10 minutos)")
    print("4. Salir")
    
    choice = input("Elige una opción (1-4): ").strip()
    
    if choice == "1":
        bot.interactive_chat()
    elif choice == "2":
        bot.auto_messages(5)
    elif choice == "3":
        bot.auto_messages(10)
    elif choice == "4":
        print("¡Adiós!")
    else:
        print("Opción no válida")

if __name__ == "__main__":
    main()
