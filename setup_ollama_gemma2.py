#!/usr/bin/env python3
"""
Setup Ollama and Gemma2 for LLM Focus System
"""

import subprocess
import requests
import time
import sys
import os

def check_ollama_installed():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Ollama is installed: {result.stdout.strip()}")
            return True
        else:
            print("Ollama is not installed")
            return False
    except FileNotFoundError:
        print("Ollama is not installed")
        return False

def install_ollama():
    """Install Ollama"""
    print("Installing Ollama...")
    
    # For Windows, download and install Ollama
    if sys.platform == "win32":
        print("Please download and install Ollama from: https://ollama.ai/download")
        print("After installation, restart this script.")
        return False
    
    # For Linux/macOS
    try:
        result = subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], capture_output=True, text=True)
        if result.returncode == 0:
            install_script = result.stdout
            subprocess.run(['sh'], input=install_script, text=True)
            return True
        else:
            print("Failed to download Ollama install script")
            return False
    except Exception as e:
        print(f"Error installing Ollama: {e}")
        return False

def check_ollama_running():
    """Check if Ollama server is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("Ollama server is running")
            return True
        else:
            print("Ollama server is not responding")
            return False
    except requests.exceptions.RequestException:
        print("Ollama server is not running")
        return False

def start_ollama_server():
    """Start Ollama server"""
    print("Starting Ollama server...")
    
    try:
        # Start Ollama in background
        subprocess.Popen(['ollama', 'serve'], 
                       stdout=subprocess.DEVNULL, 
                       stderr=subprocess.DEVNULL)
        
        # Wait for server to start
        for i in range(10):
            time.sleep(2)
            if check_ollama_running():
                print("Ollama server started successfully")
                return True
        
        print("Failed to start Ollama server")
        return False
        
    except Exception as e:
        print(f"Error starting Ollama server: {e}")
        return False

def check_gemma2_installed():
    """Check if Gemma2 is installed"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            for model in models:
                if 'gemma2' in model.get('name', '').lower():
                    print(f"Gemma2 is installed: {model['name']}")
                    return True
        
        print("Gemma2 is not installed")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error checking models: {e}")
        return False

def install_gemma2():
    """Install Gemma2 model"""
    print("Installing Gemma2 model...")
    
    try:
        # Download Gemma2 (this may take a while)
        result = subprocess.run(['ollama', 'pull', 'gemma2'], 
                               capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Gemma2 installed successfully")
            return True
        else:
            print(f"Failed to install Gemma2: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"Error installing Gemma2: {e}")
        return False

def test_gemma2():
    """Test Gemma2 functionality"""
    print("Testing Gemma2...")
    
    try:
        payload = {
            "model": "gemma2",
            "prompt": "Responde con 'OK' si puedes leer esto.",
            "stream": False,
            "options": {"max_tokens": 10}
        }
        
        response = requests.post("http://localhost:11434/api/generate", 
                               json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"Gemma2 test successful: {result.get('response', 'No response')}")
            return True
        else:
            print(f"Gemma2 test failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error testing Gemma2: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("OLLAMA & GEMMA2 SETUP")
    print("="*60)
    
    # Step 1: Check if Ollama is installed
    print("\n1. Checking Ollama installation...")
    if not check_ollama_installed():
        print("Please install Ollama first:")
        if sys.platform == "win32":
            print("- Download from: https://ollama.ai/download")
            print("- Run the installer")
            print("- Restart command prompt")
        else:
            print("- Run: curl -fsSL https://ollama.ai/install.sh | sh")
        
        response = input("\nContinue anyway? (y/n): ").lower()
        if response != 'y':
            return
    
    # Step 2: Check if Ollama server is running
    print("\n2. Checking Ollama server...")
    if not check_ollama_running():
        print("Starting Ollama server...")
        if not start_ollama_server():
            print("Failed to start Ollama server")
            print("Please run: ollama serve")
            return
    
    # Step 3: Check if Gemma2 is installed
    print("\n3. Checking Gemma2 model...")
    if not check_gemma2_installed():
        print("Installing Gemma2 model...")
        print("This may take several minutes...")
        
        if not install_gemma2():
            print("Failed to install Gemma2")
            print("Please run: ollama pull gemma2")
            return
    
    # Step 4: Test Gemma2
    print("\n4. Testing Gemma2...")
    if test_gemma2():
        print("\n" + "="*60)
        print("OLLAMA & GEMMA2 SETUP COMPLETED!")
        print("="*60)
        print("\nGemma2 is ready for the LLM Focus System")
        print("You can now run: python llm_conversation_analyzer.py")
        print("="*60)
    else:
        print("\nGemma2 test failed")
        print("Please check Ollama installation")

if __name__ == "__main__":
    main()
