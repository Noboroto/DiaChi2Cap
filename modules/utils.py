# -*- coding: utf-8 -*-
"""
Address conversion utility functions
Contains helper functions for address normalization, geocoding, and coordinate conversion
"""
import re
import requests
import urllib.parse


TEST_API_KEY = "testing-chuyen-doi-2-cap"
API_DOMAIN_PROD = "https://address-converter.io.vn"
API_DOMAIN_TEST = "http://localhost:5000"
GOONG_API_KEY = "blank" # "VUoAmeVhEf7qbje0PlPS9IatkTuqJfJtTx8FjSmY"
OPENMAP_API_KEY = "blank" # "A5PFHXxiTe780Z2GZRQjPMjQ5EQaVCsm"

MAX_BATCH_SIZE = 1000
BATCH_DELAY_SECONDS = 2
OPENMAP_RATE_LIMIT_DELAY = 0.2
MAX_RETRY_ATTEMPTS = 1000

REPLACEMENT_REQUIRES = [
    ("Quận 02", "Thành phố Thủ Đức"),
    ("Quận 2", "Thành phố Thủ Đức"),
    ("Huyện Dăk RLấp", "Huyện Đắk R'Lấp"),
    ("Xã Ea Bhôk", "Xã Ea BHốk"),
    ("Huyện Dăk Mil", "Huyện Đắk Mil"),
    ("Thành phố KonTum", "Thành phố Kon Tum"),
    ("Xã Đăk Ngo", "Xã Đắk Ngo"),
    ("Thành phố Huế", "Quận Thuận Hóa"),
    ("Tỉnh Thừa Thiên Huế", "Thành phố Huế"),
    ("Thừa Thiên Huế", "Thành phố Huế"),
    ("M'Đrăk", "M'Đrắk"),
    ("Krông Ana", "Krông A Na"),
    ("Thị trấn NT Thống Nhất", "Thị trấn Thống Nhất"),
    ("Đạ Tẻh", "Đạ Huoai"),
    ("kty1", "KTY 1"),
    ("kty2", "KTY 2"),
    ("kty4", "KTY 4"),
    ("kty5", "KTY 5"),
    ("Kty1", "KTY 1"),
    ("Kty2", "KTY 2"),
    ("Kty4", "KTY 4"),
    ("Kty5", "KTY 5"),
    ("Buk", "Búk"),
    ("Đăk", "Đắk"),
    ("Dăk", "Đắk"),
    ("Dak", "Đắk"),
    ("dăk", "đắk"),
    ("dak", "đắk"),
    ("đăk", "đắk"),
]

PRE_CONVERTED = {
    "huyện Lý Sơn, tỉnh Quảng Ngãi": "Đặc khu Lý Sơn, Tỉnh Quảng Ngãi",
    "huyện Phú Quốc, tỉnh Kiên Giang": "Đặc khu Phú Quốc, Tỉnh An Giang",
    "huyện Vân Đồn, tỉnh Quảng Ninh": "Đặc khu Vân Đồn, Tỉnh Quảng Ninh",
    "huyện Côn Đảo, tỉnh Bà Rịa - Vũng Tàu": "Đặc khu Côn Đảo, Thành phố Hồ Chí Minh",
}

def pre_convert_address(address_str):
    """
    Apply pre-conversion mapping for special administrative regions.
    Uses case-insensitive matching to handle variations in input casing.
    
    Args:
        address_str: Input address string
        
    Returns:
        tuple: (matched, converted_address)
            - matched: Boolean indicating if pre-conversion was applied
            - converted_address: Converted string if matched, otherwise original
    """
    if not address_str or address_str.strip() == "":
        return True, "Địa chỉ lỗi,"
    
    address_lower = address_str.lower()
    
    for old_pattern, new_pattern in PRE_CONVERTED.items():
        if old_pattern.lower() in address_lower:
            return True, new_pattern
    
    return False, address_str

def build_address_from_components(row: dict, use_street: bool):
    """
    Build full address string from components in data dict.
    
    Args:
        data: Dictionary with address components
        use_street: Boolean indicating whether to include street component
    Returns:
        Full address string
    """
    if isinstance(row, str):
        return row.strip()
    so_nha_duong = so_nha_cleaner(row.get('so_nha_duong', ''))
    phuong_xa = normalize_address_component(row.get('phuong_xa', ''))
    quan_huyen = normalize_address_component(row.get('quan_huyen', ''))
    tinh_thanh = normalize_address_component(row.get('tinh_thanh', ''))
    
    if phuong_xa == "" and quan_huyen == "" and tinh_thanh == "":
        return ""

    if use_street:
        return f"{so_nha_duong}, {phuong_xa}, {quan_huyen}, {tinh_thanh}".strip()
    else:
        return f"{phuong_xa}, {quan_huyen}, {tinh_thanh}".strip()



def normalize_address_component(text):
    """
    Normalize address component by trimming whitespace and removing leading zeros.
    
    Examples:
        "Phường 02" -> "Phường 2"
        "Quận 03" -> "Quận 3"
        "  Phường 10  " -> "Phường 10"
    
    Args:
        text: Address component string
        
    Returns:
        Normalized string with trimmed spaces and no leading zeros
    """
    if not text:
        return ''
    
    text = text.strip()
    
    for old, new in REPLACEMENT_REQUIRES:
        if text.lower() == old.lower():
            return new
        
    # clear leading zeros in numbers, using regex
    text = re.sub(r'(\D)0+(\d)', r'\1\2', text)
    
    for old, new in REPLACEMENT_REQUIRES:
        text = text.replace(old, new)
    
    return text


def so_nha_cleaner(text):
    """
    Remove 'số nhà' or 'Số nhà' prefix from street address and format properly.
    
    Examples:
        "số nhà 123 Đường ABC" -> "123, Đường ABC"
        "Số nhà 45" -> "45"
        "123 Đường XYZ" -> "123, Đường XYZ"
    
    Args:
        text: Street address string
        
    Returns:
        formatted_text: String with 'số nhà' prefix removed and properly formatted
    """    
    text = normalize_address_component(text).strip()

    text = text.replace("Số Nhà", "") \
          .replace("SỐ NHÀ", "") \
          .replace("số nhà", "") \
          .replace("Số nhà", "") \
          .replace(":", "") \
          .strip()
    
    if text.lower().startswith("số"):
        text = text[2:].strip()

    # Replace "Tổ dân phố \d+" with empty string
    text = re.sub(r"Tổ dân phố \d+", "", text).strip()
    text = re.sub(r"tổ dân phố \d+", "", text).strip()
    text = re.sub(r"tổ \d+", "", text).strip()
    text = re.sub(r"Tổ \d+", "", text).strip()
    text = re.sub(r"TDP \d+", "", text).strip()
    text = re.sub(r"tdp \d+", "", text).strip()
    text = re.sub(r"TDP\d+", "", text).strip()
    text = re.sub(r"tdp\d+", "", text).strip()
    text = re.sub(r"^(TDP|tdp|Tổ dân phố|tổ dân phố|Tổ|tổ)[^,]*,\s*", "", text).strip()


    # Replace "Khu phố \d+" with empty string
    text = re.sub(r"Khu phố \d+", "", text).strip()
    text = re.sub(r"khu phố \d+", "", text).strip()
    text = re.sub(r"khu \d+", "", text).strip()
    text = re.sub(r"Khu \d+", "", text).strip()
    text = re.sub(r"KP \d+", "", text).strip()
    text = re.sub(r"kp \d+", "", text).strip()
    text = re.sub(r"KP\d+", "", text).strip()
    text = re.sub(r"kp\d+", "", text).strip()
    text = re.sub(r"^(KP|kp|Khu phố|khu phố|Khu|khu)[^,]*,\s*", "", text).strip()

    # Replace "Huyện, ..." at the start with empty string
    text = re.sub(r"^(Huyện|Quận|Thị xã|Thành phố|Thành Phố|TP\.|TP|Tỉnh|Xã|Phường|Thị trấn)[^,]*,\s*", "", text).strip()
    text = re.sub(r"^(huyện|quận|thị xã|thành phố|thành phố|tp\.|tp|tỉnh|xã|phường|thị trấn)[^,]*,\s*", "", text).strip()
    
    # Replace các case như "205-207 thành "205"
    text = re.sub(r"^(\d+)-\d+\s+", r"\1 ", text).strip()


    if "," in text:
        if text[0] == ",":
            text = text[1:].strip()
        return text
    if not text or not text[0].isdigit():
        return text

    parts = text.split(" ", 1)
    if parts[0].strip() == "":
        return text.strip()
    text = ", ".join([part.strip() for part in parts if part.strip() != ""]).strip()

    return text


def geocode_address(address, goong_api_key):
    """
    Call Goong.io Geocoding API to convert address to coordinates.
    
    Args:
        address: Full address string
        goong_api_key: Goong.io API key
        
    Returns:
        tuple: (success, latitude, longitude, error_message)
    """
    if not address or goong_api_key == "blank":
        return False, None, None, "Geocoding disabled"
    
    try:
        encoded_address = urllib.parse.quote(address)
        geocode_url = f"https://rsapi.goong.io/geocode?address={encoded_address}&api_key={goong_api_key}"
        
        response = requests.get(geocode_url, timeout=10)
        
        if response.status_code != 200:
            return False, None, None, f"HTTP {response.status_code}"
        
        data = response.json()
        
        if data.get('status') != 'OK':
            return False, None, None, "No results found"
        
        results = data.get('results', [])
        if not results:
            return False, None, None, "Empty results"
        
        geometry = results[0].get('geometry', {})
        location = geometry.get('location', {})
        
        lat = location.get('lat')
        lng = location.get('lng')
        
        if lat is None or lng is None:
            return False, None, None, "No coordinates in response"
        
        return True, lat, lng, None
        
    except Exception:
        return False, None, None, "Exception"


def openmap_geocode_address(address, openmap_api_key):
    """
    Call OpenMap.vn Forward Geocoding API to convert address to coordinates.
    
    Uses Google-compatible format endpoint for consistency with existing code.
    
    Args:
        address: Full address string
        openmap_api_key: OpenMap.vn API key
        
    Returns:
        tuple: (success, latitude, longitude, error_message)
    """
    if not address or openmap_api_key == "blank":
        return False, None, None, "OpenMap geocoding disabled"
    
    try:
        encoded_address = urllib.parse.quote(address)
        geocode_url = f"https://mapapis.openmap.vn/v1/geocode/forward?address={encoded_address}&apikey={openmap_api_key}"
        
        response = requests.get(geocode_url, timeout=10)
        
        if response.status_code != 200:
            return False, None, None, f"HTTP {response.status_code}"
        
        data = response.json()
        
        if data.get('status') != 'OK':
            return False, None, None, f"Status: {data.get('status')}"
        
        results = data.get('results', [])
        if not results:
            return False, None, None, "No results"
        
        geometry = results[0].get('geometry', {})
        location = geometry.get('location', {})
        
        lat = location.get('lat')
        lng = location.get('lng')
        
        if lat is None or lng is None:
            return False, None, None, "No coordinates"
        
        return True, lat, lng, None
        
    except requests.exceptions.Timeout:
        return False, None, None, "Timeout"
    except requests.exceptions.RequestException as e:
        return False, None, None, f"Request error: {str(e)}"
    except Exception as e:
        return False, None, None, f"Exception: {str(e)}"


def convert_coordinates_to_address(coordinates_list, api_key, api_domain):
    """
    Call /api/convert-coordinate to get new addresses from coordinates (batch).
    
    Args:
        coordinates_list: List of tuples [(longitude, latitude), ...]
        api_key: Address converter API key
        api_domain: API domain (test or prod)
        
    Returns:
        list: List of tuples [(success, new_address, error_message), ...]
    """
    if not coordinates_list:
        return []
    
    try:
        coordinate_endpoint = f"{api_domain}/api/convert-coordinate"
        
        coord_objects = [{"longitude": lng, "latitude": lat} for lng, lat in coordinates_list]
        
        response = requests.post(
            coordinate_endpoint,
            json={
                "coordinates": coord_objects,
                "key": api_key
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}"
            return [(False, None, error_msg) for _ in coordinates_list]
        
        result_data = response.json()
        
        if not result_data.get("success", False):
            error = result_data.get("error", "Unknown error")
            return [(False, None, error) for _ in coordinates_list]
        
        data_list = result_data.get("data", [])
        if not data_list:
            return [(False, None, "Empty data") for _ in coordinates_list]
        
        results = []
        for i, coord_result in enumerate(data_list):
            if not coord_result.get("success", False):
                error = coord_result.get("error", "Coordinate conversion failed")
                results.append((False, None, error))
                continue
            
            ward_info = coord_result.get("wardInfo", {})
            ward_name = ward_info.get("newWardName", "")
            province_name = ward_info.get("provinceName", "")
            
            if ward_name and province_name:
                new_address = f"{ward_name}, {province_name}"
                results.append((True, new_address, None))
            else:
                results.append((False, None, "Incomplete ward info"))
        
        while len(results) < len(coordinates_list):
            results.append((False, None, "Missing result"))
        
        return results
        
    except Exception as e:
        error_msg = f"Exception: {str(e)}"
        return [(False, None, error_msg) for _ in coordinates_list]


def try_geocoding_fallback(original_address, row_data, is_multi_column, api_key, api_domain, goong_api_key, openmap_api_key):
    """
    Try to convert failed address using geocoding fallback.
    
    Process:
    1. For multi-column: prepare address from street, ward, district, province
    2. Try Goong.io geocoding API first, if unavailable try OpenMap.vn API
    3. Call coordinate conversion API to get new address
    
    Args:
        original_address: Original address string that failed
        row_data: Original row data dict (for multi-column)
        is_multi_column: Boolean indicating multi-column format
        api_key: Address converter API key
        api_domain: API domain
        goong_api_key: Goong.io API key
        openmap_api_key: OpenMap.vn API key
        
    Returns:
        dict: Result with success, converted, error fields
    """
    if goong_api_key == "blank" and openmap_api_key == "blank":
        return {
            "original": original_address,
            "converted": "",
            "error": "Geocoding disabled",
            "success": False
        }
    
    geocode_address_str = original_address
    
    if is_multi_column and row_data:
        so_nha_duong = row_data.get('so_nha_duong', '').strip()
        phuong_xa = row_data.get('phuong_xa', '').strip()
        quan_huyen = row_data.get('quan_huyen', '').strip()
        tinh_thanh = row_data.get('tinh_thanh', '').strip()

        so_nha_duong_new = so_nha_cleaner(so_nha_duong)
        row_data.set('so_nha_duong', f" {so_nha_duong_new}")
        row_data.set('so_nha_duong_new', f" {so_nha_duong_new}")
        so_nha_duong = so_nha_duong_new

        addr_parts = [p for p in [so_nha_duong, phuong_xa, quan_huyen, tinh_thanh] if p]
        geocode_address_str = ', '.join(addr_parts)
    
    geo_success = False
    lat = None
    lng = None
    geo_error = None
    
    if goong_api_key != "blank":
        geo_success, lat, lng, geo_error = geocode_address(geocode_address_str, goong_api_key)
    
    if not geo_success and openmap_api_key != "blank":
        geo_success, lat, lng, geo_error = openmap_geocode_address(geocode_address_str, openmap_api_key)
    
    if not geo_success:
        return {
            "original": original_address,
            "converted": "",
            "error": "Geocoding failed",
            "success": False
        }
    
    coord_results = convert_coordinates_to_address([(lng, lat)], api_key, api_domain)
    
    if coord_results and len(coord_results) > 0:
        coord_success, new_address, coord_error = coord_results[0]
        
        if coord_success:
            return {
                "original": original_address,
                "converted": new_address,
                "success": True,
                "geocoded": True
            }
        else:
            combined_error = f"Geocode OK but coordinate conversion failed: {coord_error}"
            return {
                "original": original_address,
                "converted": "",
                "error": combined_error,
                "success": False
            }
    else:
        return {
            "original": original_address,
            "converted": "",
            "error": "Coordinate conversion returned no results",
            "success": False
        }
