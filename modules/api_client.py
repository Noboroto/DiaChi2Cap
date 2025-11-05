# -*- coding: utf-8 -*-
"""
API client for address conversion service
Handles batch conversion and coordinate conversion
"""
import requests
import time


class AddressAPIClient:
    """Client for interacting with Address Converter API"""
    
    def __init__(self, api_key, api_domain, max_batch_size=1000, batch_delay_seconds=5):
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
        self.max_batch_size = max_batch_size
        self.batch_delay_seconds = batch_delay_seconds
        self.convert_endpoint = f"{api_domain}/api/convert-batch"
        self.coordinate_endpoint = f"{api_domain}/api/convert-coordinate"
        self.account_endpoint = f"{api_domain}/api/account-status"
    
    def convert_batch(self, addresses):
        """
        Convert a batch of addresses
        
        Args:
            addresses: List of address strings
            
        Returns:
            Response JSON from API
        """
        response = requests.post(
            self.convert_endpoint,
            json={
                "addresses": addresses,
                "key": self.api_key
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        return response.json()
    
    def convert_coordinates(self, coordinates):
        """
        Convert coordinates to addresses
        
        Args:
            coordinates: List of (longitude, latitude) tuples
            
        Returns:
            List of (success, address, error) tuples
        """
        coord_objects = [
            {"longitude": lng, "latitude": lat}
            for lng, lat in coordinates
        ]
        
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
            error_msg = result_data.get("error", "Coordinate conversion failed")
            return [(False, "", error_msg) for _ in coordinates]
        
        data = result_data.get("data", [])
        results = []
        
        for item in data:
            if item.get("success", False):
                ward_info = item.get("wardInfo", {})
                new_ward = ward_info.get("newWardName", "")
                province = ward_info.get("provinceName", "")
                new_address = f"{new_ward}, {province}" if new_ward and province else ""
                results.append((True, new_address, ""))
            else:
                error = item.get("error", "Unknown error")
                results.append((False, "", error))
        
        return results
    
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
