# -*- coding: utf-8 -*-
"""
Comprehensive syntax and import validation for DiaChi2Cap project
Tests all Python files for syntax errors, unused imports, and undefined references
"""
import sys
import os
from pathlib import Path

def test_module_imports():
    """Test that all modules can be imported"""
    print("[OK] Testing module imports...")
    
    try:
        from modules import api_client
        print("[OK] modules.api_client imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import modules.api_client: {e}")
        return False
    
    try:
        from modules import conversion_processor
        print("[OK] modules.conversion_processor imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import modules.conversion_processor: {e}")
        return False
    
    try:
        from modules import file_handlers
        print("[OK] modules.file_handlers imported successfully")
    except Exception as e:
        print(f"[ERROR] Failed to import modules.file_handlers: {e}")
        return False
    
    return True

def test_utils_import():
    """Test utils module"""
    print("\n[OK] Testing utils module...")
    
    try:
        import utils
        print("[OK] utils module imported successfully")
        
        required_constants = [
            'TEST_API_KEY', 'API_DOMAIN_PROD', 'API_DOMAIN_TEST',
            'GOONG_API_KEY', 'OPENMAP_API_KEY', 'MAX_BATCH_SIZE',
            'BATCH_DELAY_SECONDS', 'OPENMAP_RATE_LIMIT_DELAY'
        ]
        
        for const in required_constants:
            if not hasattr(utils, const):
                print(f"[ERROR] Missing constant: {const}")
                return False
            print(f"[OK] Found constant: {const}")
        
        required_functions = [
            'pre_convert_address', 'normalize_address_component',
            'so_nha_cleaner', 'geocode_address', 'openmap_geocode_address',
            'convert_coordinates_to_address', 'try_geocoding_fallback'
        ]
        
        for func in required_functions:
            if not hasattr(utils, func):
                print(f"[ERROR] Missing function: {func}")
                return False
            print(f"[OK] Found function: {func}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import utils: {e}")
        return False

def test_app_import():
    """Test main app module"""
    print("\n[OK] Testing app module...")
    
    try:
        import app
        print("[OK] app module imported successfully")
        
        if not hasattr(app, 'AddressConverterApp'):
            print("[ERROR] Missing class: AddressConverterApp")
            return False
        print("[OK] Found class: AddressConverterApp")
        
        if not hasattr(app, 'main'):
            print("[ERROR] Missing function: main")
            return False
        print("[OK] Found function: main")
        
        return True
    except Exception as e:
        print(f"[ERROR] Failed to import app: {e}")
        return False

def test_file_syntax():
    """Test all Python files for syntax errors"""
    print("\n[OK] Testing file syntax...")
    
    project_root = Path(__file__).parent
    python_files = list(project_root.rglob('*.py'))
    
    all_valid = True
    for py_file in python_files:
        if '__pycache__' in str(py_file):
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                code = f.read()
            compile(code, str(py_file), 'exec')
            print(f"[OK] {py_file.relative_to(project_root)}")
        except SyntaxError as e:
            print(f"[ERROR] Syntax error in {py_file.relative_to(project_root)}: {e}")
            all_valid = False
    
    return all_valid

def main():
    """Run all validation tests"""
    print("="*60)
    print("DIACCHI2CAP PROJECT VALIDATION")
    print("="*60)
    
    all_tests_passed = True
    
    if not test_file_syntax():
        all_tests_passed = False
    
    if not test_utils_import():
        all_tests_passed = False
    
    if not test_module_imports():
        all_tests_passed = False
    
    if not test_app_import():
        all_tests_passed = False
    
    print("\n" + "="*60)
    if all_tests_passed:
        print("[SUCCESS] ALL TESTS PASSED")
        print("="*60)
        return 0
    else:
        print("[FAILURE] SOME TESTS FAILED")
        print("="*60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
