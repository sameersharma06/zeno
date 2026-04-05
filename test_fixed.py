#!/usr/bin/env python3
import sys
import os

# Add current directory to path
sys.path.insert(0, os.getcwd())

def test_core_imports():
    try:
        from core.memory import log_event
        from core.tasks import get_tasks
        from core.brain import get_response
        print("✅ Core imports work")
        return True
    except ImportError as e:
        print(f"❌ Core imports failed: {e}")
        return False

def test_api_imports():
    try:
        from api.routes import app
        print("✅ API imports work")
        return True
    except ImportError as e:
        print(f"❌ API imports failed: {e}")
        return False

def test_agents_imports():
    try:
        from agents.router import run_agents
        print("✅ Agents imports work")
        return True
    except ImportError as e:
        print(f"❌ Agents imports failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing fixed structure...")
    
    tests = [test_core_imports, test_api_imports, test_agents_imports]
    passed = 0
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"🎯 {passed}/{len(tests)} tests passed")
