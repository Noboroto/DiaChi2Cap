# -*- coding: utf-8 -*-
"""
API client for address conversion service
Handles batch conversion and coordinate conversion
"""
import requests


class AddressAPIClient:
    """Client for interacting with Address Converter API"""
    
    def __init__(self, api_key, api_domain, maximum_addresses_per_batch=1000, batch_delay_seconds=5, maximum_coordinates_per_batch=10):
        """
        Initialize API client
        
        Args:
            api_key: API key for authentication
            api_domain: Base URL for API
            max_batch_size: Maximum addresses per batch
            batch_delay_seconds: Delay between batches
        """
        self.api_key = api_key
        self.api_domain = api_domain
        self.max_addresses_per_batch = maximum_addresses_per_batch
        self.maximum_coordinates_per_batch = maximum_coordinates_per_batch
        self.batch_delay_seconds = batch_delay_seconds
        self.convert_endpoint = f"{api_domain}/api/convert-batch"
        self.coordinate_endpoint = f"{api_domain}/api/convert-coordinate"
        self.account_endpoint = f"{api_domain}/api/account-status"
    
    def convert_batch(self, addresses):
        """
        Convert a batch of addresses
        
        Args:
            addresses: List of address strings
            use_street: Include street in conversion (default: True)
            
        Returns:
            Response JSON from API
        """
        response = requests.post(
            self.convert_endpoint,
            json={
                "addresses": addresses,
                "key": self.api_key,
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        return response.json()
    
    def convert_coordinates(self, coordinates):
        """
        Convert coordinates to addresses with batch processing
        Chia thành các batch nhỏ (max_batch_size) để tránh vượt quá giới hạn API
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            List of (success, address, error) tuples
        """
        if not coordinates:
            return []
        
        total_coords = len(coordinates)
        all_results = []
        
        for batch_start in range(0, total_coords, self.maximum_coordinates_per_batch):
            batch_end = min(batch_start + self.maximum_coordinates_per_batch, total_coords)
            batch_coords = coordinates[batch_start:batch_end]
            
            coord_objects = [
                {"longitude": lng, "latitude": lat}
                for lng, lat in batch_coords
            ]
            
            try:
                response = requests.post(
                    self.coordinate_endpoint,
                    json={
                        "coordinates": coord_objects,
                        "key": self.api_key
                    },
                    headers={"Content-Type": "application/json"},
                    timeout=60
                )
                
                result_data = response.json()
                
                if not result_data.get("success", False):
                    error_msg = result_data.get("error", "Chuyển đổi tọa độ thất bại")
                    all_results.extend([(False, "", error_msg) for _ in batch_coords])
                    continue
                
                data = result_data.get("data", [])
                
                for item in data:
                    if item.get("success", False):
                        ward_info = item.get("wardInfo", {})
                        new_ward = ward_info.get("newWardName", "")
                        province = ward_info.get("provinceName", "")
                        new_address = f"{new_ward}, {province}" if new_ward and province else ""
                        all_results.append((True, new_address, ""))
                    else:
                        error = item.get("error", "Lỗi không xác định")
                        all_results.append((False, "", error))
                
                if len(data) < len(batch_coords):
                    missing_count = len(batch_coords) - len(data)
                    all_results.extend([(False, "", "Thiếu kết quả từ API") for _ in range(missing_count)])
                    
            except Exception as e:
                error_msg = f"Lỗi không xác định: {str(e)}"
                all_results.extend([(False, "", error_msg) for _ in batch_coords])
        
        return all_results
    
    def fetch_account_info(self):
        """
        Fetch account information
        
        Returns:
            dict: Account information or None on error
        """
        try:
            response = requests.get(
                f"{self.account_endpoint}?key={self.api_key}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    return result.get("data")
            return None
        except Exception:
            return None
