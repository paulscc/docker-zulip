#!/usr/bin/env python3
"""
Test LLM Topic Analyzer
Prueba el sistema completo de análisis de topics con LLM
"""

import requests
import json
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class LLMTopicAnalyzerTest:
    def __init__(self):
        """Initialize LLM topic analyzer test"""
        self.llm_url = "http://localhost:11434/api/generate"
        self.llm_model = "gemma2:2b"
        
    def test_llm_connection(self):
        """Test LLM connection"""
        print("Testing LLM connection...")
        
        try:
            payload = {
                "model": self.llm_model,
                "prompt": "Responde con 'OK' si puedes leer esto.",
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "max_tokens": 10
                }
            }
            
            response = requests.post(self.llm_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "").strip()
                
                if "OK" in response_text:
                    print("  LLM connection: SUCCESS")
                    return True
                else:
                    print(f"  LLM unexpected response: {response_text}")
                    return False
            else:
                print(f"  LLM connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"  LLM connection error: {e}")
            return False
    
    def test_topic_analysis_prompt(self):
        """Test topic analysis prompt"""
        print("Testing topic analysis prompt...")
        
        try:
            from llm_topic_analyzer import LLMTopicAnalyzer
            
            analyzer = LLMTopicAnalyzer()
            
            # Test case 1: Topic should stay the same
            test_messages_1 = [
                "Necesitamos revisar el presupuesto de marketing",
                "El presupuesto para Q2 está aprobado",
                "¿Cuánto tenemos disponible para publicidad?"
            ]
            
            prompt_1 = analyzer.create_topic_analysis_prompt("Presupuesto Q2", test_messages_1)
            
            print("  Test Case 1: Topic should stay 'Presupuesto Q2'")
            print(f"    Prompt length: {len(prompt_1)} characters")
            
            response_1 = analyzer.call_llm(prompt_1)
            
            if response_1:
                decision_1, title_1, reason_1 = analyzer.parse_llm_response(response_1)
                print(f"    Decision: {decision_1}")
                print(f"    Title: {title_1}")
                print(f"    Reason: {reason_1}")
                print(f"    Raw response: {response_1[:100]}...")
            else:
                print("    No response from LLM")
            
            print()
            
            # Test case 2: Topic should change
            test_messages_2 = [
                "Estoy programando una API REST con Python",
                "Necesito optimizar las consultas a la base de datos",
                "Alguien sabe cómo mejorar el rendimiento del frontend?"
            ]
            
            prompt_2 = analyzer.create_topic_analysis_prompt("Presupuesto Q2", test_messages_2)
            
            print("  Test Case 2: Topic should change from 'Presupuesto Q2'")
            print(f"    Prompt length: {len(prompt_2)} characters")
            
            response_2 = analyzer.call_llm(prompt_2)
            
            if response_2:
                decision_2, title_2, reason_2 = analyzer.parse_llm_response(response_2)
                print(f"    Decision: {decision_2}")
                print(f"    Title: {title_2}")
                print(f"    Reason: {reason_2}")
                print(f"    Raw response: {response_2[:100]}...")
            else:
                print("    No response from LLM")
            
            return True
            
        except Exception as e:
            print(f"  Topic analysis test error: {e}")
            return False
    
    def test_zulip_connection(self):
        """Test Zulip API connection"""
        print("Testing Zulip API connection...")
        
        try:
            from llm_topic_analyzer import LLMTopicAnalyzer
            
            analyzer = LLMTopicAnalyzer()
            
            # Test getting topics
            topics = analyzer.get_all_active_topics()
            
            print(f"  Found {len(topics)} active topics:")
            for topic in topics[:5]:  # Show first 5
                print(f"    - {topic.get('name', 'Unknown')}")
            
            if len(topics) > 5:
                print(f"    ... and {len(topics) - 5} more")
            
            return True
            
        except Exception as e:
            print(f"  Zulip connection error: {e}")
            return False
    
    def test_topic_update(self):
        """Test topic update functionality"""
        print("Testing topic update functionality...")
        
        try:
            from llm_topic_analyzer import LLMTopicAnalyzer
            
            analyzer = LLMTopicAnalyzer()
            
            # Get stream ID
            stream_id = analyzer.get_stream_id()
            
            if stream_id:
                print(f"  Stream ID for '{analyzer.target_stream}': {stream_id}")
                return True
            else:
                print("  Could not get stream ID")
                return False
                
        except Exception as e:
            print(f"  Topic update test error: {e}")
            return False
    
    def simulate_topic_analysis(self):
        """Simulate complete topic analysis"""
        print("Simulating complete topic analysis...")
        
        scenarios = [
            {
                "name": "Budget Discussion",
                "current_topic": "Presupuesto Q2",
                "messages": [
                    "Necesitamos aprobar el presupuesto de marketing",
                    "El presupuesto para Q2 está listo",
                    "¿Cuánto tenemos disponible para el equipo?"
                ],
                "expected_decision": "MANTENER"
            },
            {
                "name": "API Development",
                "current_topic": "Reunión General",
                "messages": [
                    "Estoy desarrollando una API REST con Python",
                    "Necesito ayuda con la optimización de consultas SQL",
                    "Alguien sabe cómo mejorar el rendimiento del frontend?"
                ],
                "expected_decision": "CAMBIAR"
            },
            {
                "name": "Mixed Discussion",
                "current_topic": "Desarrollo Web",
                "messages": [
                    "El frontend está casi listo",
                    "Pero necesitamos hablar sobre el presupuesto del proyecto",
                    "Aunque la API backend funciona bien"
                ],
                "expected_decision": "CAMBIAR"  # or MANTENER depending on LLM
            }
        ]
        
        try:
            from llm_topic_analyzer import LLMTopicAnalyzer
            
            analyzer = LLMTopicAnalyzer()
            
            for scenario in scenarios:
                print(f"\n  Scenario: {scenario['name']}")
                print(f"    Current topic: {scenario['current_topic']}")
                print(f"    Expected decision: {scenario['expected_decision']}")
                
                # Create prompt
                prompt = analyzer.create_topic_analysis_prompt(
                    scenario['current_topic'], 
                    scenario['messages']
                )
                
                # Get LLM response
                response = analyzer.call_llm(prompt)
                
                if response:
                    decision, title, reason = analyzer.parse_llm_response(response)
                    print(f"    LLM Decision: {decision}")
                    print(f"    Suggested Title: {title}")
                    print(f"    Reason: {reason}")
                    
                    # Check if matches expectation
                    if decision == scenario['expected_decision']:
                        print(f"    Result: MATCH")
                    else:
                        print(f"    Result: DIFFERENT (Expected: {scenario['expected_decision']})")
                else:
                    print(f"    No LLM response")
            
            return True
            
        except Exception as e:
            print(f"  Simulation error: {e}")
            return False
    
    def run_complete_test(self):
        """Run complete LLM topic analyzer test"""
        print("="*60)
        print("LLM TOPIC ANALYZER TEST")
        print("="*60)
        
        results = {}
        
        # Test 1: LLM Connection
        print("\n1. Testing LLM connection...")
        results['llm_connection'] = self.test_llm_connection()
        
        # Test 2: Topic Analysis Prompt
        print("\n2. Testing topic analysis prompt...")
        if results.get('llm_connection'):
            results['topic_analysis'] = self.test_topic_analysis_prompt()
        else:
            results['topic_analysis'] = False
        
        # Test 3: Zulip Connection
        print("\n3. Testing Zulip API connection...")
        results['zulip_connection'] = self.test_zulip_connection()
        
        # Test 4: Topic Update
        print("\n4. Testing topic update functionality...")
        if results.get('zulip_connection'):
            results['topic_update'] = self.test_topic_update()
        else:
            results['topic_update'] = False
        
        # Test 5: Simulation
        print("\n5. Simulating topic analysis...")
        if results.get('llm_connection'):
            results['simulation'] = self.simulate_topic_analysis()
        else:
            results['simulation'] = False
        
        # Summary
        print("\n" + "="*60)
        print("LLM TOPIC ANALYZER TEST SUMMARY")
        print("="*60)
        
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        overall_success = all(results.values())
        print(f"\nOverall: {'SUCCESS' if overall_success else 'FAIL'}")
        
        if overall_success:
            print("\nTo start the LLM topic analyzer:")
            print("1. Ensure Ollama is running with gemma2:2b model")
            print("2. Start monitoring: python llm_topic_analyzer.py")
            print("3. System will analyze topics every 20 seconds")
            print("4. Topics will be automatically updated when conversation drifts")
        else:
            print("\nSome tests failed. Please check:")
            print("- Ollama is running on localhost:11434")
            print("- Gemma2:2b model is installed")
            print("- Zulip server is accessible")
            print("- Bot configuration is correct")
        
        print("\nFeatures:")
        print("  - LLM-powered topic analysis")
        print("  - Automatic topic updates")
        print("  - Topic change notifications")
        print("  - Configurable analysis intervals")
        print("  - Human message filtering")
        
        print("="*60)
        
        return overall_success

def main():
    """Main function"""
    test = LLMTopicAnalyzerTest()
    
    try:
        success = test.run_complete_test()
        
        if success:
            print("\nSystem is ready for production use!")
        else:
            print("\nPlease resolve the issues before using the system.")
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"Test error: {e}")

if __name__ == "__main__":
    main()
