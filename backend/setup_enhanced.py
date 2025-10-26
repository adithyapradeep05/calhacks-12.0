#!/usr/bin/env python3
"""
Setup script for RAGFlow Enhanced MVP Backend
This script helps set up the enhanced backend with all required services
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def install_requirements():
    """Install enhanced requirements"""
    print("\n📦 Installing enhanced requirements...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements_enhanced.txt"], 
                      check=True, capture_output=True, text=True)
        print("✅ Requirements installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install requirements: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = [
        "./storage/chroma",
        "./storage/uploads", 
        "./storage/cache"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created {directory}")

def setup_environment():
    """Setup environment variables"""
    print("\n🔧 Setting up environment...")
    
    env_file = Path(".env")
    env_example = Path("env_enhanced.example")
    
    if not env_file.exists() and env_example.exists():
        print("📋 Copying environment template...")
        with open(env_example, 'r') as f:
            content = f.read()
        with open(env_file, 'w') as f:
            f.write(content)
        print("✅ Environment file created from template")
        print("⚠️ Please edit .env file with your API keys")
    else:
        print("✅ Environment file already exists")

def check_services():
    """Check if required services are available"""
    print("\n🔍 Checking services...")
    
    services = {
        "Redis": check_redis(),
        "Supabase": check_supabase(),
        "S3": check_s3()
    }
    
    for service, status in services.items():
        if status:
            print(f"✅ {service}: Available")
        else:
            print(f"⚠️ {service}: Not configured (optional for MVP)")

def check_redis():
    """Check Redis connection"""
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def check_supabase():
    """Check if Supabase is configured"""
    return os.getenv("SUPABASE_URL") is not None

def check_s3():
    """Check if S3 is configured"""
    return os.getenv("AWS_ACCESS_KEY_ID") is not None

def create_supabase_schema():
    """Create Supabase schema if needed"""
    print("\n🗄️ Supabase schema setup...")
    
    schema_sql = """
-- Create documents table for enhanced backend
CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    category TEXT NOT NULL,
    s3_key TEXT NOT NULL,
    file_size INTEGER,
    namespace TEXT DEFAULT 'default',
    upload_time TIMESTAMP DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_documents_category ON documents(category);
CREATE INDEX IF NOT EXISTS idx_documents_namespace ON documents(namespace);
CREATE INDEX IF NOT EXISTS idx_documents_upload_time ON documents(upload_time);
"""
    
    schema_file = Path("supabase_schema.sql")
    with open(schema_file, 'w') as f:
        f.write(schema_sql)
    
    print("✅ Supabase schema file created: supabase_schema.sql")
    print("⚠️ Please run this SQL in your Supabase dashboard")

def test_imports():
    """Test if all required modules can be imported"""
    print("\n🧪 Testing imports...")
    
    required_modules = [
        "fastapi",
        "uvicorn", 
        "chromadb",
        "anthropic",
        "openai",
        "boto3",
        "redis",
        "supabase"
    ]
    
    failed_imports = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module}")
            failed_imports.append(module)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        return False
    
    print("✅ All imports successful")
    return True

def main():
    """Main setup function"""
    print("🚀 RAGFlow Enhanced MVP Backend Setup")
    print("=" * 40)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Setup environment
    setup_environment()
    
    # Test imports
    if not test_imports():
        print("❌ Setup failed at import testing")
        sys.exit(1)
    
    # Check services
    check_services()
    
    # Create Supabase schema
    create_supabase_schema()
    
    print("\n🎉 Enhanced MVP Backend setup completed!")
    print("\n📋 Next steps:")
    print("1. Edit .env file with your API keys")
    print("2. Start Redis: redis-server")
    print("3. Run Supabase schema: supabase_schema.sql")
    print("4. Start the enhanced backend: python app_enhanced.py")
    print("5. Test the backend: python test_enhanced.py")

if __name__ == "__main__":
    main()
