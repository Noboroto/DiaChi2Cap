# -*- coding: utf-8 -*-
"""
Conversion processor - Business logic for address conversion
Handles batching, pre-conversion, geocoding fallback
"""
import time
from utils import (
    normalize_address_component,
    so_nha_cleaner,
    pre_convert_address,
    geocode_address,
    openmap_geocode_address
)


class ConversionProcessor:
    """Process address conversion with batching and fallback"""
    
    def __init__(self, api_client, goong_api_key=None, openmap_api_key=None, openmap_rate_limit=0.2):
        """
        Initialize processor
        
        Args:
            api_client: AddressAPIClient instance
            goong_api_key: Goong Maps API key for geocoding
            openmap_api_key: OpenMap.vn API key for geocoding
            openmap_rate_limit: Minimum delay between OpenMap requests
        """
        self.api_client = api_client
        self.goong_api_key = goong_api_key
        self.openmap_api_key = openmap_api_key
        self.openmap_rate_limit = openmap_rate_limit
        self.last_openmap_request_time = 0
        self.stop_requested = False
    
    def request_stop(self):
        """Request to stop the conversion process"""
        self.stop_requested = True
    
    def reset_stop_flag(self):
        """Reset stop flag for new conversion"""
        self.stop_requested = False
    
    def prepare_addresses(self, data, is_multi_column):
        """
        Prepare addresses from input data
        
        Args:
            data: List of addresses or list of dicts
            is_multi_column: Boolean indicating format
            
        Returns:
            tuple: (addresses, original_data, pre_converted_indices)
        """
        addresses = []
        pre_converted_indices = {}
        original_data = None
        
        if is_multi_column:
            original_data = data
            for idx, row in enumerate(data):
                addr_parts = [
                    normalize_address_component(row.get('phuong_xa', '')),
                    normalize_address_component(row.get('quan_huyen', '')),
                    normalize_address_component(row.get('tinh_thanh', ''))
                ]
                so_nha_duong = normalize_address_component(row.get('so_nha_duong', '').strip())
                so_nha_duong_new = so_nha_cleaner(so_nha_duong)
                original_data[idx]['so_nha_duong_new'] = f" {so_nha_duong_new}"
                address = ', '.join([p for p in addr_parts if p])
                matched, converted = pre_convert_address(address)
                
                if matched:
                    pre_converted_indices[idx] = converted
                
                addresses.append(converted)
        else:
            for idx, addr in enumerate(data):
                matched, converted = pre_convert_address(addr)
                if matched:
                    pre_converted_indices[idx] = converted
                addresses.append(converted)
        
        return addresses, original_data, pre_converted_indices
    
    def process_batch(self, batch_items, skipped_indices, max_retries=10000):
        """
        Process a single batch with retry logic
        
        Args:
            batch_items: List of (index, address) tuples
            skipped_indices: Set of indices to skip
            max_retries: Maximum retry attempts
            
        Returns:
            tuple: (results_dict, successful_count, failed_count, updated_skipped)
        """
        results_dict = {}
        successful = 0
        failed = 0
        
        retry_count = 0
        
        while retry_count < max_retries and batch_items and not self.stop_requested:
            batch_addresses = [addr for idx, addr in batch_items]
            
            result_data = self.api_client.convert_batch(batch_addresses)
            
            if not result_data.get("success", False):
                error_msg = result_data.get("error", "Unknown error")
                
                if result_data.get("rateLimited", False):
                    retry_after = result_data.get("retryAfter", 0)
                    
                    for i in range(retry_after):
                        if self.stop_requested:
                            break
                        time.sleep(1)
                    if self.stop_requested:
                        break
                    continue
                else:
                    raise Exception(error_msg)
            
            data = result_data.get("data", {})
            batch_results = data.get("results", [])
            
            balance_error_indices = []
            balance_error_addrs = set()
            
            for i, result in enumerate(batch_results):
                original_idx = batch_items[i][0]
                
                if not result.get("success", False):
                    error_msg = result.get("error", "")
                    if "Số dư không đủ" in error_msg:
                        balance_error_indices.append(original_idx)
                        balance_error_addrs.add(batch_items[i][1])
                        results_dict[original_idx] = {
                            "original": result.get("original", ""),
                            "converted": "",
                            "error": "Số dư không đủ - Đã bỏ qua",
                            "success": False
                        }
                    else:
                        results_dict[original_idx] = result
                        failed += 1
                else:
                    results_dict[original_idx] = result
                    successful += 1
            
            if balance_error_indices:
                skipped_indices.update(balance_error_indices)
                
                for idx, addr in batch_items:
                    if idx not in balance_error_indices and addr in balance_error_addrs:
                        skipped_indices.add(idx)
                        results_dict[idx] = {
                            "original": addr,
                            "converted": "",
                            "error": "Số dư không đủ - Đã bỏ qua (trùng)",
                            "success": False
                        }
                
                batch_items = [(idx, addr) for idx, addr in batch_items if idx not in skipped_indices]
                
                if batch_items:
                    retry_count += 1
                    if not self.stop_requested:
                        time.sleep(1)
                    continue
                else:
                    break
            
            break
        
        return results_dict, successful, failed, skipped_indices
    
    def openmap_geocode_with_rate_limit(self, address):
        """
        Call OpenMap API with rate limiting
        
        Args:
            address: Address string to geocode
            
        Returns:
            tuple: (success, latitude, longitude, error_message)
        """
        current_time = time.time()
        time_since_last_request = current_time - self.last_openmap_request_time
        
        if time_since_last_request < self.openmap_rate_limit:
            sleep_time = self.openmap_rate_limit - time_since_last_request
            time.sleep(sleep_time)
        
        result = openmap_geocode_address(address, self.openmap_api_key)
        
        self.last_openmap_request_time = time.time()
        
        return result
    
    def geocode_fallback(self, addresses, results_dict, skipped_indices, is_multi_column, original_data):
        """
        Try geocoding for failed addresses
        
        Args:
            addresses: Original address list
            results_dict: Current results dictionary
            skipped_indices: Set of skipped indices
            is_multi_column: Boolean for format type
            original_data: Original multi-column data
            
        Returns:
            tuple: (updated_results, geocoded_success, geocoded_failed)
        """
        if not (self.goong_api_key and self.goong_api_key != "blank") and \
           not (self.openmap_api_key and self.openmap_api_key != "blank"):
            return results_dict, 0, 0
        
        total_addresses = len(addresses)
        failed_indices = [i for i in range(total_addresses) 
                        if not results_dict[i].get("success", False) 
                        and i not in skipped_indices]
        
        if not failed_indices:
            return results_dict, 0, 0
        
        geocode_tasks = []
        for idx in failed_indices:
            if self.stop_requested:
                break
            
            geocode_address_str = addresses[idx]
            
            if is_multi_column and original_data:
                row_data = original_data[idx]
                so_nha_duong = row_data.get('so_nha_duong', '').strip()
                phuong_xa = row_data.get('phuong_xa', '').strip()
                quan_huyen = row_data.get('quan_huyen', '').strip()
                tinh_thanh = row_data.get('tinh_thanh', '').strip()
                
                so_nha_duong_new = so_nha_cleaner(so_nha_duong)
                original_data[idx]['so_nha_duong_new'] = f" {so_nha_duong_new}"
                so_nha_duong = so_nha_duong_new
                
                addr_parts = [p for p in [so_nha_duong, phuong_xa, quan_huyen, tinh_thanh] if p]
                geocode_address_str = ', '.join(addr_parts)
            
            geocode_tasks.append((idx, geocode_address_str, addresses[idx]))
        
        coordinates_to_convert = []
        geocode_map = {}
        
        for idx, geocode_addr, original_addr in geocode_tasks:
            if self.stop_requested:
                break
            
            geo_success = False
            lat = None
            lng = None
            
            if self.goong_api_key and self.goong_api_key != "blank":
                geo_success, lat, lng, geo_error = geocode_address(geocode_addr, self.goong_api_key)
            
            if not geo_success and self.openmap_api_key and self.openmap_api_key != "blank":
                geo_success, lat, lng, geo_error = self.openmap_geocode_with_rate_limit(geocode_addr)
            
            if geo_success:
                coord_idx = len(coordinates_to_convert)
                coordinates_to_convert.append((lng, lat))
                geocode_map[coord_idx] = (idx, original_addr)
        
        geocoded_success = 0
        geocoded_failed = len(geocode_tasks) - len(coordinates_to_convert)
        
        if coordinates_to_convert:
            coord_results = self.api_client.convert_coordinates(coordinates_to_convert)
            
            for coord_idx, (success, new_address, error) in enumerate(coord_results):
                if coord_idx in geocode_map:
                    idx, original_addr = geocode_map[coord_idx]
                    
                    if success:
                        results_dict[idx] = {
                            "original": original_addr,
                            "converted": new_address,
                            "success": True,
                            "geocoded": True
                        }
                        geocoded_success += 1
                    else:
                        results_dict[idx] = {
                            "original": original_addr,
                            "converted": "",
                            "error": f"Geocode OK but coordinate conversion failed: {error}",
                            "success": False
                        }
                        geocoded_failed += 1
        
        return results_dict, geocoded_success, geocoded_failed
