#!/usr/bin/env python3
"""
Test LLM Focus System Complete
Tests the complete LLM-based focus monitoring system
"""

import requests
import json
import time
import threading
import subprocess
import sys
from datetime import datetime

def test_llm_connection():
    """Test LLM (Gemma2) connection"""
    print("Testing LLM connection...")
    
    try:
        payload = {
            "model": "gemma2:2b",
            "prompt": "Responde con 'OK' si puedes leer esto.",
            "stream": False,
            "options": {"max_tokens": 10}
        }
        
        response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            print(f"  LLM response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"  LLM connection failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  LLM connection error: {e}")
        return False

def test_zulip_connection():
    """Test Zulip API connection"""
    print("Testing Zulip connection...")
    
    try:
        # Load config to get API key
        with open("bot_config.json", 'r') as f:
            config = json.load(f)
        
        bot = config.get("bots", [{}])[0]  # Get first bot
        api_key = bot.get("api_key")
        
        if not api_key:
            print("  No API key found")
            return False
        
        server_url = "http://localhost"
        url = f"{server_url}/api/v1/users/me"
        headers = {
            "Authorization": f"Bearer {api_key}",
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

def start_incoming_webhook():
    """Start incoming webhook server in background"""
    print("Starting incoming webhook server...")
    
    def run_server():
        try:
            from incoming_focus_webhook import app
            app.run(host='0.0.0.0', port=5001, debug=False)
        except Exception as e:
            print(f"Error starting incoming webhook: {e}")
    
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    
    time.sleep(2)
    return server_thread

def test_incoming_webhook():
    """Test incoming webhook server"""
    print("Testing incoming webhook server...")
    
    # Test health endpoint
    try:
        response = requests.get("http://localhost:5001/health")
        
        if response.status_code == 200:
            print("  Incoming webhook health check passed")
        else:
            print(f"  Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"  Health check error: {e}")
        return False
    
    # Test webhook endpoint
    test_payload = {
        "message": "**Test message** :test:\n\nThis is a test from the LLM focus system.",
        "stream": "desarrollo",
        "topic": "test-llm-focus",
        "type": "llm_focus_reminder",
        "analysis": {
            "main_topic": "test conversation",
            "topic_change": False,
            "focus_needed": False
        }
    }
    
    try:
        response = requests.post("http://localhost:5001/webhook", json=test_payload)
        
        if response.status_code == 200:
            print("  Incoming webhook test passed")
            return True
        else:
            print(f"  Webhook test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"  Webhook test error: {e}")
        return False

def test_llm_analyzer():
    """Test LLM conversation analyzer"""
    print("Testing LLM conversation analyzer...")
    
    try:
        from llm_conversation_analyzer import LLMConversationAnalyzer
        
        analyzer = LLMConversationAnalyzer()
        
        # Test LLM connection
        if not analyzer.test_llm_connection():
            print("  LLM connection test failed")
            return False
        
        # Test analysis
        print("  Running conversation analysis test...")
        analyzer.analyze_and_act()
        
        print("  LLM analyzer test completed")
        return True
        
    except Exception as e:
        print(f"  LLM analyzer test error: {e}")
        return False

def run_system_test():
    """Run complete system test"""
    print("Running system integration test...")
    
    try:
        # Send test message to trigger LLM analysis
        from llm_conversation_analyzer import LLMConversationAnalyzer
        
        analyzer = LLMConversationAnalyzer()
        
        # Simulate messages that would trigger topic change
        test_messages = [
            "Estoy trabajando en una nueva API REST con Python y FastAPI",
            "Alguien sabe cómo optimizar queries en PostgreSQL?",
            "Qué opinan de las nuevas políticas de trabajo remoto en la empresa?",
            "Volviendo al tema técnico, necesito ayuda con Docker para mi aplicación"
        ]
        
        print("  Simulating conversation with topic changes...")
        
        # Send messages via Zulip API (if possible)
        for i, message in enumerate(test_messages):
            print(f"    Message {i+1}: {message[:50]}...")
            
            # This would normally be sent by users in Zulip
            # For testing, we'll just wait a bit
            time.sleep(1)
        
        # Run analysis
        analyzer.analyze_and_act()
        
        print("  System test completed")
        return True
        
    except Exception as e:
        print(f"  System test error: {e}")
        return False

def main():
    """Main test function"""
    print("="*70)
    print("TEST LLM FOCUS SYSTEM COMPLETE")
    print("="*70)
    
    results = {}
    
    # Test 1: LLM Connection
    print("\n1. Testing LLM (Gemma2) connection...")
    results['llm_connection'] = test_llm_connection()
    
    # Test 2: Zulip Connection
    print("\n2. Testing Zulip API connection...")
    results['zulip_connection'] = test_zulip_connection()
    
    # Test 3: Start Incoming Webhook
    print("\n3. Starting incoming webhook server...")
    try:
        server_thread = start_incoming_webhook()
        results['incoming_webhook_start'] = True
        print("  Incoming webhook server started successfully")
    except Exception as e:
        print(f"  Failed to start incoming webhook: {e}")
        results['incoming_webhook_start'] = False
    
    # Test 4: Incoming Webhook
    print("\n4. Testing incoming webhook server...")
    if results.get('incoming_webhook_start'):
        results['incoming_webhook'] = test_incoming_webhook()
    else:
        results['incoming_webhook'] = False
    
    # Test 5: LLM Analyzer
    print("\n5. Testing LLM conversation analyzer...")
    results['llm_analyzer'] = test_llm_analyzer()
    
    # Test 6: System Integration
    print("\n6. Running system integration test...")
    if all([results.get('llm_connection'), results.get('zulip_connection'), results.get('incoming_webhook')]):
        results['system_integration'] = run_system_test()
    else:
        results['system_integration'] = False
    
    # Summary
    print("\n" + "="*70)
    print("TEST RESULTS SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    # Overall result
    all_passed = all(results.values())
    print(f"\nOverall: {'PASS' if all_passed else 'FAIL'}")
    
    if all_passed:
        print("\n" + "="*70)
        print("LLM FOCUS SYSTEM READY FOR PRODUCTION!")
        print("="*70)
        print("\nTo start the complete system:")
        print("1. Start incoming webhook server:")
        print("   python incoming_focus_webhook.py")
        print("2. Start LLM conversation analyzer:")
        print("   python llm_conversation_analyzer.py")
        print("3. Send messages to #desarrollo channel in Zulip")
        print("4. System will analyze conversations every 20 seconds")
        print("5. LLM will detect topic changes and send focus reminders")
        print("\nSystem features:")
        print("- Analyzes conversations every 20 seconds")
        print("- Uses Gemma2 LLM for intelligent topic detection")
        print("- Sends contextual focus reminders via webhook")
        print("- Logs all focus events for tracking")
        print("- Provides statistics via /stats endpoint")
        print("="*70)
    else:
        print("\nSome tests failed. Please check the configuration:")
        print("- Ensure Gemma2 is running on localhost:11434")
        print("- Check Zulip server is running on localhost")
        print("- Verify bot configuration in bot_config.json")
        print("- Check network connectivity")
    
    return all_passed

if __name__ == "__main__":
    main()
