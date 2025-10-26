#!/usr/bin/env python3
"""
Simple script to start the RAGFlow backend with checks.
"""

import os
import sys
import subprocess
import requests
import time

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        print(f"Current version: {sys.version}")
        return False
    print(f"SUCCESS: Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import fastapi
        import chromadb
        import anthropic
        import openai
        print("SUCCESS: All required packages are installed")
        return True
    except ImportError as e:
        print(f"ERROR: Missing dependency: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = "backend/.env"
    if not os.path.exists(env_path):
        print("ERROR: .env file not found")
        print("Copy env.example to .env and add your API keys")
        return False
    
    with open(env_path, 'r') as f:
        content = f.read()
    
    if "OPENAI_API_KEY=your_openai_api_key_here" in content:
        print("ERROR: Please set your OpenAI API key in .env file")
        return False
    
    if "ANTHROPIC_API_KEY=your_anthropic_api_key_here" in content:
        print("ERROR: Please set your Anthropic API key in .env file")
        return False
    
    print("SUCCESS: .env file configured")
    return True

def start_backend():
    """Start the backend server"""
    print("\nStarting RAGFlow Backend...")
    print("=" * 40)
    
    # Change to backend directory
    os.chdir("backend")
    
    try:
        # Start the backend
        subprocess.run([sys.executable, "run.py"], check=True)
    except KeyboardInterrupt:
        print("\nBackend stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Backend failed to start: {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False
    
    return True

def main():
    """Main startup function"""
    print("RAGFlow Backend Startup Check")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check dependencies
    if not check_dependencies():
        return False
    
    # Check .env file
    if not check_env_file():
        return False
    
    print("\nAll checks passed! Starting backend...")
    return start_backend()

if __name__ == "__main__":
    main()

