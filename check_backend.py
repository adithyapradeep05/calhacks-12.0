#!/usr/bin/env python3
"""
Check if backend is running.
"""

import requests
import time

def check_backend():
    """Check if backend is running."""
    print("Checking Backend Status...")
    print("=" * 30)
    
    try:
        print("Testing connection to http://localhost:8000...")
        response = requests.get("http://localhost:8000/stats", timeout=2)
        print(f"SUCCESS: Backend is running (status: {response.status_code})")
        return True
    except requests.exceptions.ConnectionError:
        print("ERROR: Backend is not running")
        print("Start it with: cd backend && python run.py")
        return False
    except requests.exceptions.Timeout:
        print("ERROR: Backend is not responding (timeout)")
        print("Backend might be hanging or overloaded")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    check_backend()
