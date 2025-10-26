#!/usr/bin/env python3
"""
Check Claude configuration and API key.
"""

import os
import sys

def check_claude_config():
    """Check Claude configuration."""
    print("Checking Claude Configuration...")
    print("=" * 40)
    
    # Check environment variables
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    claude_model = os.getenv("CLAUDE_MODEL", "claude-3-sonnet-20240229")
    
    print(f"ANTHROPIC_API_KEY: {'SET' if anthropic_key else 'NOT SET'}")
    print(f"CLAUDE_MODEL: {claude_model}")
    
    if anthropic_key:
        print(f"API Key length: {len(anthropic_key)} characters")
        print(f"API Key starts with: {anthropic_key[:10]}...")
    else:
        print("ERROR: ANTHROPIC_API_KEY not found!")
        print("Make sure you have a .env file in the backend directory with:")
        print("ANTHROPIC_API_KEY=your_key_here")
    
    # Check if we can import anthropic
    try:
        import anthropic
        print("SUCCESS: anthropic module imported")
        
        if anthropic_key:
            try:
                client = anthropic.Anthropic(api_key=anthropic_key)
                print("SUCCESS: Claude client created")
            except Exception as e:
                print(f"ERROR: Failed to create Claude client: {e}")
        else:
            print("WARNING: Cannot test Claude client without API key")
            
    except ImportError:
        print("ERROR: anthropic module not installed")
        print("Run: pip install anthropic")

if __name__ == "__main__":
    check_claude_config()
