# -*- coding: utf-8 -*-
"""
Code lookup module for extracting province and ward codes
Loads province.json and ward.json to match administrative codes
"""
import json
import re
import sys
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

PROVINCE_DATA: Optional[Dict[str, Any]] = None
WARD_DATA: Optional[Dict[str, Any]] = None


def get_data_dir():
    """Get the data directory path, handling PyInstaller bundled exe"""
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = Path(getattr(sys, '_MEIPASS', '.'))
    else:
        base_path = Path(__file__).parent.parent
    
    return base_path / "data"


def load_json_data():
    """Load province and ward JSON data"""
    global PROVINCE_DATA, WARD_DATA
    
    if PROVINCE_DATA is None or WARD_DATA is None:
        data_dir = get_data_dir()
        
        with open(data_dir / "province.json", 'r', encoding='utf-8') as f:
            PROVINCE_DATA = json.load(f)
        
        with open(data_dir / "ward.json", 'r', encoding='utf-8') as f:
            WARD_DATA = json.load(f)


def normalize_text(text: str) -> str:
    """
    Normalize text for matching: lowercase, remove accents variations
    """
    if not text:
        return ""
    
    text = text.lower().strip()
    
    replacements = {
        'đ': 'd',
        'á': 'a', 'à': 'a', 'ả': 'a', 'ã': 'a', 'ạ': 'a',
        'ă': 'a', 'ắ': 'a', 'ằ': 'a', 'ẳ': 'a', 'ẵ': 'a', 'ặ': 'a',
        'â': 'a', 'ấ': 'a', 'ầ': 'a', 'ẩ': 'a', 'ẫ': 'a', 'ậ': 'a',
        'é': 'e', 'è': 'e', 'ẻ': 'e', 'ẽ': 'e', 'ẹ': 'e',
        'ê': 'e', 'ế': 'e', 'ề': 'e', 'ể': 'e', 'ễ': 'e', 'ệ': 'e',
        'í': 'i', 'ì': 'i', 'ỉ': 'i', 'ĩ': 'i', 'ị': 'i',
        'ó': 'o', 'ò': 'o', 'ỏ': 'o', 'õ': 'o', 'ọ': 'o',
        'ô': 'o', 'ố': 'o', 'ồ': 'o', 'ổ': 'o', 'ỗ': 'o', 'ộ': 'o',
        'ơ': 'o', 'ớ': 'o', 'ờ': 'o', 'ở': 'o', 'ỡ': 'o', 'ợ': 'o',
        'ú': 'u', 'ù': 'u', 'ủ': 'u', 'ũ': 'u', 'ụ': 'u',
        'ư': 'u', 'ứ': 'u', 'ừ': 'u', 'ử': 'u', 'ữ': 'u', 'ự': 'u',
        'ý': 'y', 'ỳ': 'y', 'ỷ': 'y', 'ỹ': 'y', 'ỵ': 'y',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    return text


def extract_province_name(address: str) -> Optional[str]:
    """
    Extract province name from converted address
    Examples:
    - "Thành phố Hồ Chí Minh" -> "Hồ Chí Minh"
    - "Tỉnh Đà Nẵng" -> "Đà Nẵng"
    """
    if not address:
        return None
    
    parts = [p.strip() for p in address.split(',')]
    if not parts:
        return None
    
    last_part = parts[-1].strip()
    
    prefixes = [
        'Thành phố ',
        'Tỉnh ',
        'TP ',
        'TP. ',
    ]
    
    for prefix in prefixes:
        if last_part.startswith(prefix):
            return last_part[len(prefix):].strip()
    
    return last_part


def extract_ward_name(address: str) -> Optional[str]:
    """
    Extract ward name from converted address
    Examples:
    - "Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh" -> "Bến Nghé"
    - "Xã Tân Phú, Huyện Củ Chi, TP HCM" -> "Tân Phú"
    """
    if not address:
        return None
    
    parts = [p.strip() for p in address.split(',')]
    if not parts:
        return None
    
    first_part = parts[0].strip()
    
    prefixes = [
        'Phường ',
        'Xã ',
        'Thị trấn ',
        'P. ',
        'X. ',
        'TT. ',
    ]
    
    for prefix in prefixes:
        if first_part.startswith(prefix):
            return first_part[len(prefix):].strip()
    
    return first_part


def find_province_code(province_name: str) -> Optional[str]:
    """
    Find province code from province name
    """
    if not province_name:
        return None
    
    load_json_data()
    
    if PROVINCE_DATA is None:
        return None
    
    normalized_search = normalize_text(province_name)
    
    for code, data in PROVINCE_DATA.items():
        name = data.get('name', '')
        name_with_type = data.get('name_with_type', '')
        
        if normalized_search == normalize_text(name):
            return code
        
        if normalized_search == normalize_text(name_with_type):
            return code
        
        name_normalized = normalize_text(name)
        if name_normalized and normalized_search in name_normalized:
            return code
    
    return None


def find_ward_code(ward_name: str, province_code: str) -> Optional[str]:
    """
    Find ward code from ward name and province code
    """
    if not ward_name or not province_code:
        return None
    
    load_json_data()
    
    if WARD_DATA is None:
        return None
    
    normalized_search = normalize_text(ward_name)
    
    for code, data in WARD_DATA.items():
        parent_code = data.get('parent_code', '')
        if parent_code != province_code:
            continue
        
        name = data.get('name', '')
        name_with_type = data.get('name_with_type', '')
        
        if normalized_search == normalize_text(name):
            return code
        
        if normalized_search == normalize_text(name_with_type):
            return code
        
        name_normalized = normalize_text(name)
        if name_normalized and normalized_search in name_normalized:
            return code
    
    return None


def extract_codes_from_address(converted_address: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Extract both province and ward codes from a converted address
    
    Args:
        converted_address: Full converted address string
        
    Returns:
        tuple: (province_code, ward_code)
    """
    if not converted_address or converted_address.startswith("LỖI"):
        return None, None
    
    province_name = extract_province_name(converted_address)
    province_code = find_province_code(province_name) if province_name else None
    
    ward_name = extract_ward_name(converted_address)
    ward_code = find_ward_code(ward_name, province_code) if ward_name and province_code else None
    
    return province_code, ward_code
