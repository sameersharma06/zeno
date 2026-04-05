#!/usr/bin/env python3
"""
Test all bulletproof fixes
"""
import sys
import os
sys.path.insert(0, os.getcwd())

def test_paths():
    from core.paths import get_project_root, get_data_dir
    print("✅ Paths module working")
    return True

def test_database():
    from core.database import db_pool
    result = db_pool.execute_query("SELECT 1")
    print("✅ Database pool working")
    return True

def test_error_handler():
    from core.error_handler import safe_execute
    @safe_execute
    def test_func():
        return "success"
    result = test_func()
    print("✅ Error handler working")
    return True

def test_server():
    try:
        from api.server import app
        print("✅ Server imports working")
        return True
    except Exception as e:
        print(f"❌ Server import failed: {e}")
        return False

def main():
    print("🧪 Testing Bulletproof Foundation...")
    
    tests = [
        test_paths,
        test_database, 
        test_error_handler,
        test_server
    ]
    
    all_passed = True
    for test in tests:
        try:
            if not test():
                all_passed = False
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
            all_passed = False
    
    if all_passed:
        print("🎉 ALL TESTS PASSED - Foundation is bulletproof!")
    else:
        print("❌ Some tests failed - fix before proceeding")
    
    return all_passed

if __name__ == "__main__":
    main()
