#!/usr/bin/env python3
"""
Verify RAGFlow setup is correct.
"""

import os
import sys
import subprocess

def check_file_exists(filepath, description):
    """Check if a file exists and report status."""
    if os.path.exists(filepath):
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} (NOT FOUND)")
        return False

def check_directory_structure():
    """Check if the directory structure is correct."""
    print("Checking directory structure...")
    print("=" * 40)
    
    required_files = [
        ("backend/requirements.txt", "Backend requirements"),
        ("backend/app.py", "Backend application"),
        ("backend/run.py", "Backend startup script"),
        ("backend/env.example", "Environment example"),
        ("frontend/package.json", "Frontend package.json"),
    ]
    
    all_good = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_good = False
    
    return all_good

def check_python_version():
    """Check Python version."""
    print("\nChecking Python version...")
    print("=" * 40)
    
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version.split()[0]} (3.8+ required)")
        return True
    else:
        print(f"❌ Python {sys.version.split()[0]} (3.8+ required)")
        return False

def check_dependencies():
    """Check if dependencies can be imported."""
    print("\nChecking dependencies...")
    print("=" * 40)
    
    dependencies = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("chromadb", "ChromaDB"),
        ("anthropic", "Anthropic"),
        ("openai", "OpenAI"),
        ("pydantic", "Pydantic"),
    ]
    
    all_good = True
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}: Available")
        except ImportError:
            print(f"❌ {name}: Not installed")
            all_good = False
    
    return all_good

def main():
    """Main verification function."""
    print("RAGFlow Setup Verification")
    print("=" * 50)
    
    # Check directory structure
    if not check_directory_structure():
        print("\n❌ Directory structure is incomplete")
        print("Make sure you're in the correct directory and all files are present")
        return False
    
    # Check Python version
    if not check_python_version():
        print("\n❌ Python version is too old")
        print("Please upgrade to Python 3.8 or higher")
        return False
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Some dependencies are missing")
        print("Run: cd backend && pip install -r requirements.txt")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 Setup verification completed successfully!")
    print("You can now run: cd backend && python run.py")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    main()

