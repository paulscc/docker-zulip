#!/usr/bin/env python3
"""
Test Focus Monitor System
Tests the complete focus monitoring system
"""

import requests
import json
import time
import threading
from tecnologia_focus_monitor import TecnologiaFocusMonitor
from focus_webhook import FocusWebhookServer

def test_webhook_server():
    """Test the webhook server"""
    print("Testing webhook server...")
    
    # Test data
    test_payload = {
        "message": "**@all Mantengamos el foco** :point_up:\n\n**Tema original:** Desarrollo API\n**Nuevo tema:** Políticas empresa\n\n*Test message*",
        "stream": "desarrollo",
        "topic": "recordatorio-foco",
        "type": "focus_reminder"
    }
    
    try:
        response = requests.post("http://localhost:5000/webhook", json=test_payload)
        
        if response.status_code == 200:
            print("  Webhook server responded successfully")
            return True
        else:
            print(f"  Webhook server error: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  Webhook server test failed: {e}")
        return False

def test_focus_monitor():
    """Test the focus monitor"""
    print("Testing focus monitor...")
    
    monitor = TecnologiaFocusMonitor()
    
    # Test topic detection
    test_messages = [
        "Estoy trabajando con React y TypeScript en el frontend",
        "Alguien sabe cómo optimizar el rendimiento de PostgreSQL?",
        "Qué opinan de las nuevas políticas de trabajo remoto?",
        "Volviendo a la API, necesito ayuda con la autenticación JWT",
        "El deployment en Kubernetes está fallando"
    ]
    
    print("  Testing topic detection:")
    for i, message in enumerate(test_messages):
        print(f"    Message {i+1}: {message[:50]}...")
        
        if monitor.detect_topic_change(message):
            new_topic = monitor.extract_topic_summary(message)
            print(f"      -> Topic change detected: {new_topic}")
            monitor.current_topic = new_topic
            monitor.topic_keywords = monitor.extract_topic_keywords(message)
        else:
            print(f"      -> Same topic, no change")
    
    return True

def test_zulip_connection():
    """Test Zulip API connection"""
    print("Testing Zulip connection...")
    
    monitor = TecnologiaFocusMonitor()
    
    if not monitor.monitor_bot.get('api_key'):
        print("  No API key found in config")
        return False
    
    try:
        server_url = "http://localhost"
        url = f"{server_url}/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {monitor.monitor_bot['api_key']}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(url, headers=headers, verify=False)
        
        if response.status_code == 200:
            user_data = response.json()
            print(f"  Connected as: {user_data.get('full_name', 'Unknown')}")
            return True
        else:
            print(f"  Connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  Connection error: {e}")
        return False

def start_webhook_server():
    """Start webhook server in background"""
    print("Starting webhook server...")
    
    def run_server():
        from focus_webhook import app
        app.run(host='0.0.0.0', port=5000, debug=False)
    
    # Start server in background thread
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    # Wait for server to start
    time.sleep(2)
    
    return server_thread

def main():
    """Main test function"""
    print("="*60)
    print("TEST FOCUS MONITOR SYSTEM")
    print("="*60)
    
    results = {}
    
    # Test 1: Zulip Connection
    print("\n1. Testing Zulip API connection...")
    results['zulip_connection'] = test_zulip_connection()
    
    # Test 2: Start Webhook Server
    print("\n2. Starting webhook server...")
    try:
        server_thread = start_webhook_server()
        results['webhook_server_start'] = True
        print("  Webhook server started successfully")
    except Exception as e:
        print(f"  Failed to start webhook server: {e}")
        results['webhook_server_start'] = False
    
    # Test 3: Webhook Server
    print("\n3. Testing webhook server...")
    if results.get('webhook_server_start'):
        results['webhook_server'] = test_webhook_server()
    else:
        results['webhook_server'] = False
    
    # Test 4: Focus Monitor
    print("\n4. Testing focus monitor...")
    results['focus_monitor'] = test_focus_monitor()
    
    # Summary
    print("\n" + "="*60)
    print("TEST RESULTS SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    
    if all_passed:
        print("\n" + "="*60)
        print("SYSTEM READY FOR PRODUCTION!")
        print("="*60)
        print("\nTo start the complete system:")
        print("1. Start webhook server: python focus_webhook.py")
        print("2. Start focus monitor: python tecnologia_focus_monitor.py")
        print("3. Send messages to #desarrollo channel")
        print("4. Monitor will send focus reminders when topic changes")
        print("="*60)
    else:
        print("\nSome tests failed. Please check the configuration.")
    
    return all_passed

if __name__ == "__main__":
    main()
