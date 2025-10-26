#!/usr/bin/env python3
"""
Test script to validate Docker configuration files
without actually running Docker containers
"""

import yaml
import os
import sys
from pathlib import Path

def test_docker_compose():
    """Test docker-compose.yml syntax"""
    print("🔍 Testing docker-compose.yml...")
    
    try:
        with open('docker-compose.yml', 'r') as f:
            compose_config = yaml.safe_load(f)
        
        # Check required services
        required_services = ['redis', 'ragflow-backend', 'nginx']
        services = compose_config.get('services', {})
        
        for service in required_services:
            if service not in services:
                print(f"❌ Missing service: {service}")
                return False
            else:
                print(f"✅ Service {service} found")
        
        # Check Redis configuration
        redis_config = services['redis']
        if redis_config.get('image') == 'redis:7-alpine':
            print("✅ Redis image configured correctly")
        else:
            print("❌ Redis image not configured")
            return False
        
        # Check port mappings
        if '6379:6379' in redis_config.get('ports', []):
            print("✅ Redis port 6379 configured")
        else:
            print("❌ Redis port not configured")
            return False
        
        # Check backend configuration
        backend_config = services['ragflow-backend']
        if backend_config.get('build', {}).get('context') == './backend':
            print("✅ Backend build context configured")
        else:
            print("❌ Backend build context not configured")
            return False
        
        if '8000:8000' in backend_config.get('ports', []):
            print("✅ Backend port 8000 configured")
        else:
            print("❌ Backend port not configured")
            return False
        
        # Check Nginx configuration
        nginx_config = services['nginx']
        if nginx_config.get('image') == 'nginx:alpine':
            print("✅ Nginx image configured correctly")
        else:
            print("❌ Nginx image not configured")
            return False
        
        if '80:80' in nginx_config.get('ports', []):
            print("✅ Nginx port 80 configured")
        else:
            print("❌ Nginx port not configured")
            return False
        
        print("✅ docker-compose.yml is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error parsing docker-compose.yml: {e}")
        return False

def test_dockerfile():
    """Test Dockerfile syntax"""
    print("\n🔍 Testing backend/Dockerfile...")
    
    dockerfile_path = Path('backend/Dockerfile')
    if not dockerfile_path.exists():
        print("❌ Dockerfile not found")
        return False
    
    try:
        with open(dockerfile_path, 'r') as f:
            content = f.read()
        
        # Check for required instructions
        required_instructions = ['FROM', 'WORKDIR', 'COPY', 'RUN', 'EXPOSE', 'CMD']
        for instruction in required_instructions:
            if instruction in content:
                print(f"✅ {instruction} instruction found")
            else:
                print(f"❌ {instruction} instruction missing")
                return False
        
        # Check Python base image
        if 'FROM python:3.11-slim' in content:
            print("✅ Python 3.11 base image configured")
        else:
            print("❌ Python base image not configured correctly")
            return False
        
        # Check port exposure
        if 'EXPOSE 8000' in content:
            print("✅ Port 8000 exposed")
        else:
            print("❌ Port 8000 not exposed")
            return False
        
        print("✅ Dockerfile is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading Dockerfile: {e}")
        return False

def test_nginx_config():
    """Test nginx.conf syntax"""
    print("\n🔍 Testing nginx/nginx.conf...")
    
    nginx_path = Path('nginx/nginx.conf')
    if not nginx_path.exists():
        print("❌ nginx.conf not found")
        return False
    
    try:
        with open(nginx_path, 'r') as f:
            content = f.read()
        
        # Check for required sections
        required_sections = ['events', 'http', 'upstream', 'server']
        for section in required_sections:
            if section in content:
                print(f"✅ {section} section found")
            else:
                print(f"❌ {section} section missing")
                return False
        
        # Check upstream configuration
        if 'upstream ragflow_backend' in content:
            print("✅ Upstream configuration found")
        else:
            print("❌ Upstream configuration missing")
            return False
        
        # Check proxy configuration
        if 'proxy_pass http://ragflow_backend' in content:
            print("✅ Proxy pass configuration found")
        else:
            print("❌ Proxy pass configuration missing")
            return False
        
        print("✅ nginx.conf is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading nginx.conf: {e}")
        return False

def test_dockerignore():
    """Test .dockerignore file"""
    print("\n🔍 Testing .dockerignore...")
    
    dockerignore_path = Path('.dockerignore')
    if not dockerignore_path.exists():
        print("❌ .dockerignore not found")
        return False
    
    try:
        with open(dockerignore_path, 'r') as f:
            content = f.read()
        
        # Check for important exclusions
        important_exclusions = ['__pycache__', 'node_modules', '.git', 'storage/']
        for exclusion in important_exclusions:
            if exclusion in content:
                print(f"✅ {exclusion} excluded")
            else:
                print(f"⚠️  {exclusion} not excluded (may be intentional)")
        
        print("✅ .dockerignore is valid")
        return True
        
    except Exception as e:
        print(f"❌ Error reading .dockerignore: {e}")
        return False

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'docker-compose.yml',
        'backend/Dockerfile',
        'nginx/nginx.conf',
        '.dockerignore',
        'backend/requirements_enhanced.txt',
        'backend/app_enhanced.py'
    ]
    
    all_exist = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_exist = False
    
    return all_exist

def main():
    """Run all tests"""
    print("🐳 RAGFlow Docker Configuration Test")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_docker_compose,
        test_dockerfile,
        test_nginx_config,
        test_dockerignore
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All Docker configuration tests passed!")
        print("\n📋 Next steps:")
        print("1. Install Docker: https://docs.docker.com/get-docker/")
        print("2. Run: ./setup_docker.sh")
        print("3. Test: curl http://localhost:8000/health")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
