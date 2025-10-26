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
    
    # Check environment variables (enhanced app has better fallbacks)
    embed_provider = os.getenv("EMBED_PROVIDER", "OPENAI")
    
    print(f"Embed Provider: {embed_provider}")
    
    # Warn about missing API keys but don't exit (enhanced app has fallbacks)
    if embed_provider == "OPENAI" and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  WARNING: OPENAI_API_KEY not set, using fallback embedding")
    elif embed_provider == "GEMINI" and not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  WARNING: GOOGLE_API_KEY not set, using fallback embedding")
    
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  WARNING: ANTHROPIC_API_KEY not set, Claude responses will be limited")
    
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
