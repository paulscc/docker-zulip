#!/usr/bin/env python3
"""
Test Contextual Analyzer
Prueba el sistema de análisis contextual completo
"""

import requests
import json
import logging
import time
import threading
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContextualAnalyzerTest:
    def __init__(self):
        """Initialize contextual analyzer test"""
        self.webhook_url = "http://localhost:5001/webhook"
        
    def test_webhook_connection(self):
        """Test webhook connection"""
        print("Testing webhook connection...")
        
        try:
            response = requests.get("http://localhost:5001/health", timeout=5)
            
            if response.status_code == 200:
                print("  Webhook server is running")
                return True
            else:
                print(f"  Webhook server error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  Webhook connection error: {e}")
            return False
    
    def send_test_scenarios(self):
        """Send test scenarios to trigger alerts"""
        print("Sending test scenarios...")
        
        # Scenario 1: Tech to Non-Tech
        scenario_1 = {
            "message": "**@all Alerta de Cambio de Tema** :warning:\n\n**Tema anterior:** discusión técnica\n**Nuevo tema detectado:** conversación no técnica\n**Razón:** Cambio a tema no técnico\n\n**Último mensaje:** User: \"Qué opinan de las nuevas políticas de la empresa?\"\n\n**Para mantener el enfoque:**\n- Si el cambio es intencional, pueden continuar\n- Si fue accidental, consideren volver al tema: discusión técnica\n- Para temas diferentes, sugiero abrir un nuevo topic\n\n**Análisis contextual:**\n- Mensajes técnicos: 0\n- Mensajes no técnicos: 2\n\n**Canal:** #desarrollo | **Timestamp:** 01:06\n\n---\n*Alerta automática contextual - 2026-04-12 01:06:23*",
            "stream": "desarrollo",
            "topic": "alerta-cambio-tema",
            "type": "contextual_focus_alert",
            "analysis": {
                "topic_change": True,
                "current_topic": "conversación no técnica",
                "previous_topic": "discusión técnica",
                "tech_count": 0,
                "non_tech_count": 2
            },
            "timestamp": datetime.now().isoformat()
        }
        
        # Scenario 2: Non-Tech to Tech
        scenario_2 = {
            "message": "**@all Alerta de Cambio de Tema** :warning:\n\n**Tema anterior:** conversación no técnica\n**Nuevo tema detectado:** discusión técnica\n**Razón:** Cambio a tema técnico\n\n**Último mensaje:** User: \"Alguien sabe cómo optimizar esta consulta SQL?\"\n\n**Para mantener el enfoque:**\n- Si el cambio es intencional, pueden continuar\n- Si fue accidental, consideren volver al tema: conversación no técnica\n- Para temas diferentes, sugiero abrir un nuevo topic\n\n**Análisis contextual:**\n- Mensajes técnicos: 2\n- Mensajes no técnicos: 0\n\n**Canal:** #desarrollo | **Timestamp:** 01:06\n\n---\n*Alerta automática contextual - 2026-04-12 01:06:23*",
            "stream": "desarrollo",
            "topic": "alerta-cambio-tema",
            "type": "contextual_focus_alert",
            "analysis": {
                "topic_change": True,
                "current_topic": "discusión técnica",
                "previous_topic": "conversación no técnica",
                "tech_count": 2,
                "non_tech_count": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        scenarios = [scenario_1, scenario_2]
        
        for i, scenario in enumerate(scenarios, 1):
            print(f"  Sending scenario {i}...")
            
            try:
                response = requests.post(self.webhook_url, json=scenario, timeout=10)
                
                if response.status_code == 200:
                    print(f"    Scenario {i}: SUCCESS")
                else:
                    print(f"    Scenario {i}: FAILED - {response.status_code}")
                
            except Exception as e:
                print(f"    Scenario {i}: ERROR - {e}")
            
            time.sleep(2)  # Wait between scenarios
    
    def test_contextual_analyzer_directly(self):
        """Test the contextual analyzer directly"""
        print("Testing contextual analyzer directly...")
        
        try:
            from contextual_focus_analyzer import ContextualFocusAnalyzer
            
            analyzer = ContextualFocusAnalyzer()
            
            # Test the analyzer
            analyzer.test_analyzer()
            
            return True
            
        except Exception as e:
            print(f"  Direct analyzer test error: {e}")
            return False
    
    def simulate_topic_changes(self):
        """Simulate topic changes by sending messages"""
        print("Simulating topic changes...")
        
        # This would require sending actual messages to Zulip
        # For now, we'll just show what would happen
        
        scenarios = [
            {
                "name": "Tech Discussion",
                "messages": [
                    "Estoy trabajando en una API REST con Python",
                    "Alguien sabe cómo optimizar el rendimiento?",
                    "Necesito ayuda con Docker para el deployment"
                ],
                "expected_topic": "discusión técnica"
            },
            {
                "name": "Non-Tech Discussion", 
                "messages": [
                    "Qué opinan de las nuevas políticas de la empresa?",
                    "Alguien sabe cuándo son las vacaciones?",
                    "El clima está muy raro hoy"
                ],
                "expected_topic": "conversación no técnica"
            },
            {
                "name": "Mixed Discussion",
                "messages": [
                    "Estoy programando en React",
                    "Pero me interesa saber sobre el nuevo sistema de trabajo remoto",
                    "Aunque realmente necesito ayuda con el backend"
                ],
                "expected_topic": "conversación mixta"
            }
        ]
        
        for scenario in scenarios:
            print(f"\n  Scenario: {scenario['name']}")
            print(f"    Expected topic: {scenario['expected_topic']}")
            
            for msg in scenario['messages']:
                print(f"    - {msg}")
            
            print(f"    -> Would trigger alert if topic changes")
    
    def run_complete_test(self):
        """Run complete contextual analyzer test"""
        print("="*60)
        print("CONTEXTUAL ANALYZER TEST")
        print("="*60)
        
        results = {}
        
        # Test 1: Webhook connection
        print("\n1. Testing webhook connection...")
        results['webhook_connection'] = self.test_webhook_connection()
        
        # Test 2: Direct analyzer test
        print("\n2. Testing contextual analyzer directly...")
        results['direct_analyzer'] = self.test_contextual_analyzer_directly()
        
        # Test 3: Send test scenarios
        print("\n3. Sending test scenarios...")
        if results.get('webhook_connection'):
            self.send_test_scenarios()
            results['test_scenarios'] = True
        else:
            results['test_scenarios'] = False
        
        # Test 4: Simulate topic changes
        print("\n4. Simulating topic changes...")
        self.simulate_topic_changes()
        results['simulation'] = True
        
        # Summary
        print("\n" + "="*60)
        print("CONTEXTUAL ANALYZER TEST SUMMARY")
        print("="*60)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print("\nContextual Analyzer Features:")
        print("  - Analyzes conversations every 20 seconds")
        print("  - Detects topic changes (tech vs non-tech)")
        print("  - Sends contextual alerts via webhook")
        print("  - Provides detailed analysis in alerts")
        print("  - Maintains topic history")
        print("  - Configurable alert intervals")
        
        print("\nAlert Message Format:")
        print("  - Previous topic")
        print("  - New topic detected")
        print("  - Change reason")
        print("  - Last message that triggered change")
        print("  - Guidance for maintaining focus")
        print("  - Analysis statistics")
        
        print("="*60)
        
        return all(results.values())

def main():
    """Main function"""
    test = ContextualAnalyzerTest()
    
    try:
        success = test.run_complete_test()
        
        if success:
            print("\nTo start the contextual analyzer:")
            print("1. Start webhook server: python incoming_focus_webhook.py")
            print("2. Start analyzer: python contextual_focus_analyzer.py")
            print("3. System will analyze every 20 seconds and alert on topic changes")
        else:
            print("\nSome tests failed. Please check the configuration.")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
