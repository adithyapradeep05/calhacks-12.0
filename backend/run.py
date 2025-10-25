#!/usr/bin/env python3
"""
Startup script for RAGFlow backend.
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, skipping .env loading")

if __name__ == "__main__":
    import uvicorn
    
    # Check if required environment variables are set based on provider
    embed_provider = os.getenv("EMBED_PROVIDER", "GEMINI")
    
    if embed_provider == "OPENAI":
        required_vars = ["OPENAI_API_KEY"]
    else:
        required_vars = ["GOOGLE_API_KEY"]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"ERROR: Missing required environment variables for {embed_provider}: {missing_vars}")
        print("Please set them in your .env file or environment")
        sys.exit(1)
    
    print("Starting RAGFlow Backend...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Embed Provider: {embed_provider}")
    
    if embed_provider == "OPENAI":
        print(f"OpenAI API Key: {'Set' if os.getenv('OPENAI_API_KEY') else 'Missing'}")
        print(f"OpenAI Embed Model: {os.getenv('OPENAI_EMBED_MODEL', 'text-embedding-3-small')}")
        print(f"Google API Key: {'Not needed' if not os.getenv('GOOGLE_API_KEY') else 'Set but not used'}")
    else:
        print(f"Google API Key: {'Set' if os.getenv('GOOGLE_API_KEY') else 'Missing'}")
        print(f"Gemini Model: {os.getenv('GEMINI_EMBED_MODEL', 'models/text-embedding-004')}")
        print(f"OpenAI API Key: {'Not needed' if not os.getenv('OPENAI_API_KEY') else 'Set but not used'}")
    
    print(f"Claude Model: {os.getenv('CLAUDE_MODEL', 'claude-3-sonnet-20240229')}")
    
    print(f"Anthropic API Key: {'Set' if os.getenv('ANTHROPIC_API_KEY') else 'Missing'}")
    print(f"Chunk Size: {os.getenv('CHUNK_SIZE', '800')}")
    print(f"Chunk Overlap: {os.getenv('CHUNK_OVERLAP', '150')}")
    print()
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
