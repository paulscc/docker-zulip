#!/usr/bin/env python3
"""
Demo Webhook Kafka System
Send test messages to trigger the complete webhook + Kafka flow
"""

import requests
import json
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WebhookKafkaDemo:
    def __init__(self):
        """Initialize webhook Kafka demo"""
        # Using one of the working bots from config
        self.bot_email = "nnnnn-bot@midt.127.0.0.1.nip.io"
        self.api_key = "MBlc4lZ9EognR87LLZXMRC2w6vLZco4c"
        self.server_url = "https://midt.127.0.0.1.nip.io"
        
    def send_test_message(self, stream: str, topic: str, content: str) -> bool:
        """Send a test message to Zulip"""
        try:
            url = f"{self.server_url}/api/v1/messages"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "type": "stream",
                "to": stream,
                "topic": topic,
                "content": content
            }
            
            # Disable SSL verification for self-signed certs
            response = requests.post(
                url, 
                headers=headers, 
                json=payload,
                verify=False
            )
            
            if response.status_code == 200:
                logger.info(f"Message sent to {stream}/{topic}")
                return True
            else:
                logger.error(f"Error sending message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False
    
    def send_multiple_messages(self, stream: str, topic: str, count: int = 12):
        """Send multiple messages to trigger webhook"""
        messages = [
            "Este es el mensaje número {} para probar el sistema de webhooks con Kafka.",
            "El sistema detectará cuando hay {}+ mensajes no leídos y generará un resumen.",
            "Los resúmenes se procesarán con Ollama y se publicarán automáticamente.",
            "Este flujo demuestra la integración entre Zulip, Kafka y Ollama.",
            "Cada mensaje es parte de la conversación que será resumida.",
            "La tecnología de Kafka permite un procesamiento asíncrono y escalable.",
            "Los webhooks automatizan el proceso de detección y respuesta.",
            "Ollama genera resúmenes inteligentes usando modelos de lenguaje.",
            "Todo el sistema funciona en conjunto para proporcionar valor.",
            "Los resúmenes ayudan a mantenerse actualizado con conversaciones largas.",
            "Esta es una demostración práctica de microservicios en acción.",
            "El último mensaje completa el conjunto para activar el webhook."
        ]
        
        logger.info(f"Sending {count} messages to {stream}/{topic}")
        
        for i in range(count):
            message_content = messages[i % len(messages)].format(i + 1, count)
            message_content += f"\n\nEnviado a las: {datetime.now().strftime('%H:%M:%S')}"
            
            success = self.send_test_message(stream, topic, message_content)
            if success:
                logger.info(f"  Message {i+1}/{count} sent successfully")
            else:
                logger.error(f"  Failed to send message {i+1}/{count}")
            
            time.sleep(1)  # Small delay between messages
        
        return True
    
    def run_demo(self):
        """Run the complete webhook Kafka demo"""
        print("="*70)
        print("WEBHOOK KAFKA DEMO")
        print("="*70)
        
        print("\nThis demo will:")
        print("1. Send multiple messages to a Zulip stream")
        print("2. Trigger the outgoing webhook when threshold is reached")
        print("3. Send messages to Kafka topic 'zulip-unread-messages'")
        print("4. Process messages with Kafka summary processor")
        print("5. Generate summaries using Ollama")
        print("6. Publish summaries to Kafka topic 'zulip-summaries'")
        print("7. Incoming webhook consumes summaries and publishes to Zulip")
        
        print("\nCurrent running services:")
        print("- webhook_service_kafka.py (port 8080)")
        print("- kafka_summary_processor.py (consuming unread messages)")
        print("- outgoing_webhook.py (monitoring streams)")
        print("- incoming_webhook.py (consuming summaries)")
        
        print("\nSending test messages...")
        
        # Send messages to trigger webhook
        stream = "general"
        topic = "chat"
        
        success = self.send_multiple_messages(stream, topic, 12)
        
        if success:
            print(f"\nMessages sent to {stream}/{topic}")
            print("The webhook system should now:")
            print("1. Detect the unread messages (threshold: 10)")
            print("2. Send them to Kafka for processing")
            print("3. Generate summaries with Ollama")
            print("4. Publish summaries back to Zulip")
            print("\nCheck the terminal windows where the services are running!")
            print("Summary should appear in: #general/resumen-chat")
        else:
            print("\nFailed to send some messages. Check the logs.")
        
        print("\n" + "="*70)
        print("DEMO COMPLETED")
        print("="*70)

def main():
    """Main function"""
    demo = WebhookKafkaDemo()
    demo.run_demo()

if __name__ == "__main__":
    main()
