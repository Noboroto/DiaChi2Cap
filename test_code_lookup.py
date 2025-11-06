# -*- coding: utf-8 -*-
"""
Test script for code_lookup module
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from modules.code_lookup import (
    extract_codes_from_address,
    find_province_code,
    find_ward_code
)

def test_province_lookup():
    """Test province code lookup"""
    print("\n[TEST] Province code lookup:")
    
    test_cases = [
        ("Hồ Chí Minh", "79"),
        ("Thành phố Hồ Chí Minh", "79"),
        ("Hà Nội", "01"),
        ("Đà Nẵng", "48"),
    ]
    
    for province_name, expected_code in test_cases:
        result = find_province_code(province_name)
        status = "[OK]" if result == expected_code else "[FAIL]"
        print(f"{status} '{province_name}' -> {result} (expected: {expected_code})")

def test_ward_lookup():
    """Test ward code lookup"""
    print("\n[TEST] Ward code lookup:")
    
    test_cases = [
        ("Bến Thành", "79", "26743"),
        ("Bến Cát", "79", "25813"),
    ]
    
    for ward_name, province_code, expected_code in test_cases:
        result = find_ward_code(ward_name, province_code)
        status = "[OK]" if result == expected_code else "[FAIL]"
        print(f"{status} '{ward_name}' (province: {province_code}) -> {result} (expected: {expected_code})")

def test_full_address_extraction():
    """Test full address code extraction"""
    print("\n[TEST] Full address code extraction:")
    
    test_cases = [
        (
            "Phường Bến Thành, Quận 1, Thành phố Hồ Chí Minh",
            ("79", "26743")
        ),
        (
            "Phường Bến Cát, Thành phố Hồ Chí Minh",
            ("79", "25813")
        ),
        (
            "Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng",
            ("48", None)
        ),
    ]
    
    for address, (expected_province, expected_ward) in test_cases:
        province_code, ward_code = extract_codes_from_address(address)
        
        province_status = "[OK]" if province_code == expected_province else "[FAIL]"
        ward_status = "[OK]" if ward_code == expected_ward or expected_ward is None else "[FAIL]"
        
        print(f"{province_status} Province: {province_code} (expected: {expected_province})")
        print(f"  {ward_status} Ward: {ward_code} (expected: {expected_ward})")
        print(f"  Address: {address[:50]}...")

def test_error_cases():
    """Test error handling"""
    print("\n[TEST] Error handling:")
    
    test_cases = [
        "LỖI: Không tìm thấy địa chỉ",
        "",
        None,
    ]
    
    for address in test_cases:
        province_code, ward_code = extract_codes_from_address(address)
        status = "[OK]" if province_code is None and ward_code is None else "[FAIL]"
        print(f"{status} Error case '{address}' -> ({province_code}, {ward_code})")

if __name__ == "__main__":
    print("=" * 60)
    print("TESTING CODE LOOKUP MODULE")
    print("=" * 60)
    
    try:
        test_province_lookup()
        test_ward_lookup()
        test_full_address_extraction()
        test_error_cases()
        
        print("\n" + "=" * 60)
        print("[SUCCESS] All tests completed!")
        print("=" * 60)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
