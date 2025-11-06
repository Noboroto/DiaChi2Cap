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
OPENMAP_API_KEY =  "A5PFHXxiTe780Z2GZRQjPMjQ5EQaVCsm"

MAX_ADDRESS_BATCH_SIZE = 1000
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
    ("Thị trấn NT Việt Trung", "Thị trấn Việt Trung"), 
    ("Thị trấn NT", "Thị trấn"),
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
        return True, "[LỖI] Địa chỉ sai cú pháp,"
    
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

    if use_street and so_nha_duong.strip() != "":
        return f"{so_nha_duong}, {phuong_xa}, {quan_huyen}, {tinh_thanh}".strip()
    
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
    if text[0] == ",":
        return text[1:].strip()
    
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

    # Remove "Tổ dân phố" variants (case-insensitive)
    text = re.sub(r"Tổ dân phố \d+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"tổ \d+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"TDP\s*\d+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"^(TDP|Tổ dân phố|Tổ)[^,]*,\s*", "", text, flags=re.IGNORECASE).strip()

    # Remove "Khu phố" variants (case-insensitive)
    text = re.sub(r"Khu phố \d+", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"KP\s*\d+", "", text, flags=re.IGNORECASE).strip()

    text = re.sub(r"^(KP|Khu phố)[^,]*,\s*", "", text, flags=re.IGNORECASE).strip()

    # Replace "Huyện, ..." at the start with empty string (case-insensitive)
    text = re.sub(r"^(Huyện|Quận|Thị xã|Thành phố|TP\.|TP|Tỉnh|Xã|Phường|Thị trấn)[^,]*,\s*", "", text, flags=re.IGNORECASE).strip()
    
    # Replace các case như "`205-207`` hoặc `205 - 207`` thành "205"
    # Nếu có số trong text mới thực hiện
    if re.search(r"\d", text):
        text = re.sub(r"^(\d+)\s*[-]\s*\d+", r"\1", text).strip()


    if "," in text:
        if text[0] == ",":
            text = text[1:].strip()

        parts = text.split(",", 1)
        parts = [part.strip() for part in parts if part.strip() != ""]
        return ", ".join(parts).strip()
    
    # Nếu text có patterm "Thôn ...." hoặc "Thị trấn ....", giữ nguyên và return
    if re.search(r"^(Thôn|Thị trấn|Ấp)\s+", text.strip(), re.IGNORECASE):
        return text.strip()

    parts = text.split(" ", 1)
    if parts[0].strip() == "":
        return text.strip()
    if re.search(r"\d", parts[0]) and len(parts) > 1:
      text = ", ".join([part.strip() for part in parts if part.strip() != ""]).strip()

    text = text.replace("KDC,", "KDC").strip()
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
        return False, None, None, "Geocoding bị vô hiệu hóa"
    
    try:
        encoded_address = urllib.parse.quote(address)
        geocode_url = f"https://rsapi.goong.io/geocode?address={encoded_address}&api_key={goong_api_key}"
        
        response = requests.get(geocode_url, timeout=10)
        
        if response.status_code != 200:
            return False, None, None, f"HTTP {response.status_code}"
        
        data = response.json()
        
        if data.get('status') != 'OK':
            return False, None, None, "Không tìm thấy kết quả"
        
        results = data.get('results', [])
        if not results:
            return False, None, None, "Kết quả trống"
        
        geometry = results[0].get('geometry', {})
        location = geometry.get('location', {})
        
        lat = location.get('lat')
        lng = location.get('lng')
        
        if lat is None or lng is None:
            return False, None, None, "Không có tọa độ trong phản hồi"
        
        return True, lat, lng, None
        
    except Exception:
        return False, None, None, "Lỗi không xác định"
