# -*- coding: utf-8 -*-
"""
Conversion processor - Business logic for address conversion
Handles batching, pre-conversion, geocoding fallback
"""
import time
import requests
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed
from modules.utils import (
    pre_convert_address,
    build_address_from_components
)


class ConversionProcessor:
    """Process address conversion with batching and fallback"""
    
    def __init__(self, api_client, goong_api_key=None, openmap_api_key=None, openmap_rate_limit=0.2, progress_callback=None):
        """
        Initialize the conversion processor
        
        Args:
            api_client: API client instance
            goong_api_key: Goong API key for geocoding
            openmap_api_key: OpenMap API key for geocoding
            openmap_rate_limit: Rate limit delay for OpenMap API
            progress_callback: Callback function for progress updates
        """
        self.api_client = api_client
        self.goong_api_key = goong_api_key
        self.openmap_api_key = openmap_api_key
        self.openmap_rate_limit = openmap_rate_limit
        self.last_openmap_request_time = 0
        self.stop_requested = False
        self.progress_callback = progress_callback
    
    def request_stop(self):
        """Request to stop the conversion process"""
        self.stop_requested = True
    
    def reset_stop_flag(self):
        """Reset stop flag for new conversion"""
        self.stop_requested = False

    def _log_progress(self, message):
        """Log progress message via callback if available"""
        if self.progress_callback:
            self.progress_callback(message)
    
    def _log_timing(self, step_name, elapsed_time):
        """Ghi log thời gian thực hiện của từng bước"""
        self._log_progress(f"\n[THỜI GIAN] {step_name}: {elapsed_time:.2f} giây")
    
    def prepare_addresses(self, data, is_multi_column):
        """
        Bước 1: Chuẩn bị địa chỉ với tiền xử lý song song
        Lưu trữ cả 2 phiên bản: có tên đường và không có tên đường
        Sử dụng ThreadPoolExecutor để xử lý song song
        
        Args:
            data: Danh sách địa chỉ hoặc danh sách dict
            is_multi_column: Boolean cho biết định dạng
            
        Returns:
            tuple: (addresses_with_street, addresses_no_street, original_data, pre_converted_indices)
        """
        step_start = time.time()
        
        addresses_with_street = []
        addresses_no_street = []
        pre_converted_indices = {}
        original_data = None
        
        if is_multi_column:
            original_data = data
            
            def process_multi_column_row(idx_row):
                idx, row = idx_row
                
                addr_with_street = build_address_from_components(row, use_street=True)
                addr_no_street = build_address_from_components(row, use_street=False)
                matched, converted = pre_convert_address(addr_with_street)
                
                return idx, converted, matched, row, addr_with_street, addr_no_street
            
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(process_multi_column_row, (idx, row)): idx 
                          for idx, row in enumerate(data)}
                
                results = {}
                for future in as_completed(futures):
                    idx, converted, matched, updated_row, addr_with, addr_no = future.result()
                    results[idx] = (converted, matched, addr_with, addr_no)
                    original_data[idx] = updated_row
                
                for idx in range(len(data)):
                    converted, matched, addr_with, addr_no = results[idx]
                    if matched:
                        pre_converted_indices[idx] = converted
                    addresses_with_street.append(converted)
                    addresses_no_street.append(addr_no)
        else:
            def process_single_address(idx_addr):
                idx, addr = idx_addr
                matched, converted = pre_convert_address(addr)
                return idx, converted, matched
            
            with ThreadPoolExecutor() as executor:
                futures = {executor.submit(process_single_address, (idx, addr)): idx 
                          for idx, addr in enumerate(data)}
                
                results = {}
                for future in as_completed(futures):
                    idx, converted, matched = future.result()
                    results[idx] = (converted, matched)
                
                for idx in range(len(data)):
                    converted, matched = results[idx]
                    if matched:
                        pre_converted_indices[idx] = converted
                    addresses_with_street.append(converted)
                    addresses_no_street.append(converted)
        
        elapsed = time.time() - step_start
        self._log_timing("Bước 1 (Chuẩn bị dữ liệu)", elapsed)
        self._log_progress(f"[BƯỚC 1] Đã chuẩn bị {len(addresses_with_street)} địa chỉ")
        
        return addresses_with_street, addresses_no_street, original_data, pre_converted_indices

    def process_single_parallel(self, addresses, skipped_indices):
        """
        Bước 2: Xử lý địa chỉ theo nhóm
        Nhóm đầu tiên: 10 địa chỉ để kiểm tra nhanh
        Các nhóm tiếp theo: 100 địa chỉ mỗi nhóm
        
        Args:
            addresses: Danh sách địa chỉ cần xử lý
            skipped_indices: Tập hợp vị trí các địa chỉ đã được chuyển đổi sẵn
            
        Returns:
            tuple: (results_dict, successful_count, failed_count, failed_indices_set)
        """
        step_start = time.time()
        results_dict = {}
        total_successful = 0
        total_failed = 0
        failed_indices_set = set()
        
        indices_to_process = [i for i in range(len(addresses)) if i not in skipped_indices]
        
        if not indices_to_process:
            elapsed = time.time() - step_start
            self._log_timing("Bước 2 (Xử lý chi tiết)", elapsed)
            return results_dict, total_successful, total_failed, failed_indices_set
        
        total_to_process = len(indices_to_process)
        self._log_progress(f"[BƯỚC 2] Đang xử lý {total_to_process} địa chỉ...")
        
        FIRST_BATCH_SIZE = 10
        REGULAR_BATCH_SIZE = 100
        
        batch_configs = []
        if total_to_process <= FIRST_BATCH_SIZE:
            batch_configs.append((0, total_to_process))
        else:
            batch_configs.append((0, FIRST_BATCH_SIZE))
            
            remaining_start = FIRST_BATCH_SIZE
            while remaining_start < total_to_process:
                batch_end = min(remaining_start + REGULAR_BATCH_SIZE, total_to_process)
                batch_configs.append((remaining_start, batch_end))
                remaining_start = batch_end
        
        total_batches = len(batch_configs)
        
        for batch_num, (batch_start, batch_end) in enumerate(batch_configs, 1):
            if self.stop_requested:
                self._log_progress("[DỪNG] Bước 2 bị gián đoạn")
                for idx in indices_to_process[batch_end:]:
                    failed_indices_set.add(idx)
                break
            
            batch_indices = indices_to_process[batch_start:batch_end]
            batch_addresses = [addresses[idx] for idx in batch_indices]
            batch_size = len(batch_indices)
            
            start_pos = batch_indices[0] + 1
            end_pos = batch_indices[-1] + 1
            
            if batch_num == 1:
                self._log_progress(f"[Nhóm đầu tiên] Đang xử lý {batch_size} địa chỉ để kiểm tra (từ {start_pos} đến {end_pos})...")
            else:
                self._log_progress(f"[Nhóm {batch_num}/{total_batches}] Đang xử lý địa chỉ từ {start_pos} đến {end_pos}...")
            
            try:
                result_data = self.api_client.convert_batch(batch_addresses)
                
                if not result_data.get("success", False):
                    api_error = result_data.get("error", "Không thể kết nối API")
                    self._log_progress(f"[LỖI] {api_error}")
                    
                    for idx in batch_indices:
                        results_dict[idx] = {
                            "original": addresses[idx],
                            "converted": "",
                            "success": False,
                            "retryCount": 1,
                            "error": api_error
                        }
                        total_failed += 1
                        failed_indices_set.add(idx)
                    continue
                
                batch_results = result_data.get("data", {}).get("results", [])
                successful = 0
                failed = 0
                
                for i, result in enumerate(batch_results):
                    if i < len(batch_indices):
                        idx = batch_indices[i]
                        
                        if result.get("success", False):
                            results_dict[idx] = {
                                "original": addresses[idx],
                                "converted": result.get("converted", ""),
                                "success": True,
                                "retryCount": 1
                            }
                            successful += 1
                            total_successful += 1
                        else:
                            error_msg = result.get("error", "Lỗi không xác định")
                            results_dict[idx] = {
                                "original": addresses[idx],
                                "converted": "",
                                "success": False,
                                "retryCount": 1,
                                "error": error_msg
                            }
                            failed += 1
                            total_failed += 1
                            failed_indices_set.add(idx)
                
                for i in range(len(batch_results), len(batch_indices)):
                    idx = batch_indices[i]
                    results_dict[idx] = {
                        "original": addresses[idx],
                        "converted": "",
                        "success": False,
                        "retryCount": 1,
                        "error": "Không nhận được kết quả từ API"
                    }
                    failed += 1
                    total_failed += 1
                    failed_indices_set.add(idx)
                
                processed_so_far = batch_end
                self._log_progress(f"\tHoàn thành {processed_so_far}/{total_to_process} - {successful} thành công, {failed} thất bại")
                    
            except Exception as e:
                self._log_progress(f"[LỖI] Nhóm {batch_num}: {str(e)}")
                for idx in batch_indices:
                    results_dict[idx] = {
                        "original": addresses[idx],
                        "converted": "",
                        "success": False,
                        "retryCount": 1,
                        "error": f"Lỗi xử lý: {str(e)}"
                    }
                    total_failed += 1
                    failed_indices_set.add(idx)
        
        elapsed = time.time() - step_start
        self._log_timing("Bước 2 (Xử lý chi tiết)", elapsed)
        
        if total_successful > 0 or total_failed > 0:
            self._log_progress(f"[BƯỚC 2] Tổng kết: {total_successful} thành công, {total_failed} thất bại")
        
        return results_dict, total_successful, total_failed, failed_indices_set

    def process_batch_retry(self, addresses, results_dict, failed_indices_set):
        """
        Bước 3: Xử lý lại địa chỉ bị lỗi theo nhóm
        Gửi nhiều địa chỉ cùng lúc để xử lý nhanh
        Nếu số lượng kết quả không khớp, sẽ tự động thử lại cho các địa chỉ còn thiếu
        
        Args:
            addresses: Danh sách địa chỉ cần xử lý
            results_dict: Kết quả đã có từ bước trước
            failed_indices_set: Tập hợp vị trí các địa chỉ bị lỗi
            
        Returns:
            tuple: (results_dict, successful_count, failed_count, failed_indices_set)
        """
        from modules.utils import BATCH_DELAY_SECONDS, MAX_ADDRESS_BATCH_SIZE
        
        step_start = time.time()
        successful = 0
        failed = 0
        new_failed_set = set()
        
        if not failed_indices_set:
            elapsed = time.time() - step_start
            self._log_timing("Bước 3 (Xử lý 3 cấp cơ bản)", elapsed)
            return results_dict, successful, failed, new_failed_set
        
        failed_list = sorted(list(failed_indices_set))
        total_to_retry = len(failed_list)
        
        self._log_progress(f"[BƯỚC 3] Đang xử lý lại {total_to_retry} địa chỉ bị lỗi...")
        
        batch_num = 0
        total_batches = (total_to_retry + MAX_ADDRESS_BATCH_SIZE - 1) // MAX_ADDRESS_BATCH_SIZE
        
        while failed_list:
            if self.stop_requested:
                self._log_progress("[DỪNG] Bước 3 bị gián đoạn")
                for idx in failed_list:
                    new_failed_set.add(idx)
                break
            
            batch_num += 1
            batch_size = min(MAX_ADDRESS_BATCH_SIZE, len(failed_list))
            batch_indices = failed_list[:batch_size]
            batch_addresses = [addresses[idx] for idx in batch_indices]
            
            start_pos = batch_indices[0] + 1
            end_pos = batch_indices[-1] + 1
            self._log_progress(f"[Nhóm {batch_num}/{total_batches}] Đang xử lý địa chỉ từ {start_pos} đến {end_pos}...")
            
            try:
                result_data = self.api_client.convert_batch(batch_addresses)
                
                if not result_data.get("success", False):
                    api_error = result_data.get("error", "Không thể kết nối API")
                    self._log_progress(f"[LỖI] {api_error}")
                    for idx in batch_indices:
                        results_dict[idx] = {
                            "original": results_dict[idx]["original"],
                            "converted": "",
                            "success": False,
                            "retryCount": 2,
                            "error": api_error
                        }
                        failed += 1
                        new_failed_set.add(idx)
                    failed_list = failed_list[batch_size:]
                    continue
                
                batch_results = result_data.get("data", {}).get("results", [])
                
                if len(batch_results) != len(batch_addresses):
                    successfully_processed_indices = []
                    
                    for i, result in enumerate(batch_results):
                        if i < len(batch_indices):
                            idx = batch_indices[i]
                            
                            if result.get("success", False):
                                results_dict[idx] = {
                                    "original": results_dict[idx]["original"],
                                    "converted": result.get("converted", ""),
                                    "success": True,
                                    "retryCount": 2
                                }
                                successful += 1
                                successfully_processed_indices.append(i)
                            else:
                                error_msg = result.get("error", "Lỗi không xác định")
                                results_dict[idx] = {
                                    "original": results_dict[idx]["original"],
                                    "converted": "",
                                    "success": False,
                                    "retryCount": 2,
                                    "error": error_msg
                                }
                                failed += 1
                                new_failed_set.add(idx)
                                successfully_processed_indices.append(i)
                    
                    failed_list = [batch_indices[i] for i in range(len(batch_indices)) 
                                   if i not in successfully_processed_indices]
                    
                    if failed_list:
                        missing_count = len(failed_list)
                        self._log_progress(f"\tPhát hiện {missing_count} địa chỉ chưa được xử lý, đang thử lại...")
                else:
                    for i, result in enumerate(batch_results):
                        idx = batch_indices[i]
                        
                        if result.get("success", False):
                            results_dict[idx] = {
                                "original": results_dict[idx]["original"],
                                "converted": result.get("converted", ""),
                                "success": True,
                                "retryCount": 2
                            }
                            successful += 1
                        else:
                            error_msg = result.get("error", "Lỗi không xác định")
                            results_dict[idx] = {
                                "original": results_dict[idx]["original"],
                                "converted": "",
                                "success": False,
                                "retryCount": 2,
                                "error": error_msg
                            }
                            failed += 1
                            new_failed_set.add(idx)
                    
                    failed_list = failed_list[batch_size:]
            
            except Exception as e:
                self._log_progress(f"[LỖI] Nhóm {batch_num}: {str(e)}")
                for idx in batch_indices:
                    results_dict[idx] = {
                        "original": results_dict[idx]["original"],
                        "converted": "",
                        "success": False,
                        "retryCount": 2,
                        "error": str(e)
                    }
                    failed += 1
                    new_failed_set.add(idx)
                failed_list = failed_list[batch_size:]
            
            if failed_list and not self.stop_requested:
                time.sleep(BATCH_DELAY_SECONDS)
        
        elapsed = time.time() - step_start
        self._log_timing("Bước 3 (Xử lý 3 cấp cơ bản)", elapsed)
        
        if successful > 0 or failed > 0:
            self._log_progress(f"[BƯỚC 3] {successful} thành công, {failed} thất bại")
        
        return results_dict, successful, failed, new_failed_set
  
    def geocode_fallback_openmap_goong(self, addresses_with_street, addresses_no_street, results_dict, failed_indices_set):
        """
        Bước 4-6: Xử lý dự phòng bằng geocoding
        Mỗi bước CHỈ xử lý các địa chỉ BỊ LỖI từ bước trước
        Theo dõi failed_indices_set để tránh overhead
        
        Args:
            addresses_with_street: Danh sách địa chỉ có tên đường (đã lưu)
            addresses_no_street: Danh sách địa chỉ không có tên đường (đã lưu)
            results_dict: Kết quả hiện tại
            failed_indices_set: Tập hợp vị trí địa chỉ bị lỗi từ bước 2.3
            
        Returns:
            tuple: (updated_results_dict, total_geocoded_success)
        """
        total_geocoded_success = 0
        total_addresses = len(addresses_with_street)
        
        if self.stop_requested:
            return results_dict, total_geocoded_success
        
        if self.openmap_api_key and self.openmap_api_key != "blank":
            step_start = time.time()
            self._log_progress("[BƯỚC 4] Tìm kiếm tọa độ qua OpenMap (có tên đường)")
            results_dict, success_count, failed_indices_set = self._geocode_stage_openmap_goong(
                addresses_with_street, addresses_no_street, results_dict, failed_indices_set,
                use_street=True, use_openmap=True, retry_count=3
            )
            elapsed = time.time() - step_start
            self._log_timing("Bước 4 (Tìm tọa độ OpenMap có tên đường)", elapsed)
            
            total_geocoded_success += success_count
            current_success_total = len(results_dict)
            remaining = total_addresses - current_success_total
            
            self._log_progress(f"[BƯỚC 4] {success_count} thành công, {len(failed_indices_set)} thất bại")
            self._log_progress(f"Bước này: {success_count} thành công, {len(failed_indices_set)} thất bại")
            self._log_progress(f"Tổng lũy kế: {current_success_total} thành công, {remaining} còn lại")
        
            if not self.stop_requested and failed_indices_set:
                step_start = time.time()
                self._log_progress("[BƯỚC 5] Tìm kiếm tọa độ qua OpenMap (không có tên đường)")
                results_dict, success_count, failed_indices_set = self._geocode_stage_openmap_goong(
                    addresses_with_street, addresses_no_street, results_dict, failed_indices_set,
                    use_street=False, use_openmap=True, retry_count=4
                )
                elapsed = time.time() - step_start
                self._log_timing("Bước 5 (Tìm tọa độ OpenMap không tên đường)", elapsed)
                
                total_geocoded_success += success_count
                current_success_total = len(results_dict)
                remaining = total_addresses - current_success_total
                
                
                self._log_progress(f"[BƯỚC 5] {success_count} thành công, {len(failed_indices_set)} thất bại")
                self._log_progress(f"Bước này: {success_count} thành công, {len(failed_indices_set)} thất bại")
                self._log_progress(f"Tổng lũy kế: {current_success_total} thành công, {remaining} còn lại")
    
        if not self.stop_requested and self.goong_api_key and self.goong_api_key != "blank" and failed_indices_set:
            step_start = time.time()
            self._log_progress("[BƯỚC 6] Tìm kiếm tọa độ qua Goong (có tên đường)")
            results_dict, success_count, failed_indices_set = self._geocode_stage_openmap_goong(
                addresses_with_street, addresses_no_street, results_dict, failed_indices_set,
                use_street=True, use_openmap=False, retry_count=5
            )
            elapsed = time.time() - step_start
            self._log_timing("Bước 6 (Tìm tọa độ Goong có tên đường)", elapsed)
            
            total_geocoded_success += success_count
            current_success_total = len(results_dict)
            remaining = total_addresses - current_success_total
            
            self._log_progress(f"[BƯỚC 6] {success_count} thành công, {len(failed_indices_set)} thất bại")
            self._log_progress(f"Bước này: {success_count} thành công, {len(failed_indices_set)} thất bại")
            self._log_progress(f"Tổng lũy kế: {current_success_total} thành công, {remaining} còn lại")
    
        return results_dict, total_geocoded_success
    
    def _geocode_stage_openmap_goong(self, addresses_with_street, addresses_no_street, results_dict, failed_indices_set,
                                      use_street, use_openmap, retry_count):
        """
        Single geocoding stage with batch coordinate conversion every 10 addresses
        Count success within main loop, track remaining failures
        
        Args:
            addresses_with_street: List of addresses with street (CACHED)
            addresses_no_street: List of addresses without street (CACHED)
            results_dict: Results dictionary to update
            failed_indices_set: Set of failed indices (pre-computed)
            use_street: Boolean to use with-street or no-street version
            use_openmap: Boolean to use OpenMap (else Goong)
            retry_count: Retry count for this stage
            
        Returns:
            tuple: (updated_results_dict, success_count, new_failed_indices_set)
        """
        if not failed_indices_set or self.stop_requested:
            return results_dict, 0, failed_indices_set
        
        BATCH_SIZE = 10
        total_tasks = len(failed_indices_set)
        self._log_progress(f"\tĐang xử lý {total_tasks} địa chỉ bị lỗi")
        
        coordinates_to_convert = []
        coord_index_map = {}
        processed = 0
        total_success_count = 0
        new_failed_indices = failed_indices_set.copy()
        
        addresses_to_use = addresses_with_street if use_street else addresses_no_street
        
        failed_indices_list = list(failed_indices_set)
        
        for idx in failed_indices_list:
            if self.stop_requested:
                break
            
            geocode_addr = addresses_to_use[idx]
            
            processed += 1
            
            if use_openmap:
                success, lat, lng, _ = self._openmap_geocode_with_rate_limit(geocode_addr)
            else:
                success, lat, lng, _ = self._goong_geocode_address(geocode_addr)
            
            if success:
                coord_idx = len(coordinates_to_convert)
                coordinates_to_convert.append((lng, lat))
                coord_index_map[coord_idx] = idx
            
            if len(coordinates_to_convert) >= BATCH_SIZE or processed == total_tasks:
                if coordinates_to_convert:
                    batch_size = len(coordinates_to_convert)
                    self._log_progress(f"\t  Lấy được {batch_size} tọa độ, đang chuyển đổi sang địa chỉ 2 cấp...")
                    
                    try:
                        coord_results = self.api_client.convert_coordinates(coordinates_to_convert)
                        
                        batch_success = 0
                        batch_failed = 0
                        
                        for coord_idx, (convert_success, new_address, _) in enumerate(coord_results):
                            if coord_idx in coord_index_map:
                                idx = coord_index_map[coord_idx]
                                
                                if convert_success and new_address:
                                    original_addr = results_dict[idx].get("original", addresses_with_street[idx])
                                    results_dict[idx] = {
                                        "original": original_addr,
                                        "converted": new_address,
                                        "success": True,
                                        "geocoded": True,
                                        "retryCount": retry_count
                                    }
                                    batch_success += 1
                                    total_success_count += 1
                                    new_failed_indices.discard(idx)
                                else:
                                    batch_failed += 1
                                    if "retryCount" not in results_dict[idx]:
                                        results_dict[idx]["retryCount"] = retry_count
                        
                        self._log_progress(f"\t  Chuyển đổi: {batch_success} thành công, {batch_failed} lỗi")
                        
                    except Exception as e:
                        self._log_progress(f"\t  [LỖI] Chuyển đổi tọa độ: {str(e)}")
                    
                    coordinates_to_convert = []
                    coord_index_map = {}
            
            if processed % 10 == 0 or processed == total_tasks:
                self._log_progress(f"\t  Tiến độ tìm tọa độ: {processed}/{total_tasks}")
        
        failed_count = len(new_failed_indices)
        self._log_progress(f"\t[Tổng kết] {total_success_count} thành công, {failed_count} còn lỗi")
        
        return results_dict, total_success_count, new_failed_indices
    
    def _openmap_geocode_address(self, address):
        """
        Call OpenMap.vn Forward Geocoding API to convert address to coordinates.
        
        Uses Google-compatible format endpoint for consistency with existing code.
        
        Args:
            address: Full address string
            
        Returns:
            tuple: (success, latitude, longitude, error_message)
        """
        if not address or self.openmap_api_key == "blank":
            return False, None, None, "OpenMap geocoding bị vô hiệu hóa"
        
        try:
            encoded_address = urllib.parse.quote(address)
            geocode_url = f"https://mapapis.openmap.vn/v1/geocode/forward?address={encoded_address}&apikey={self.openmap_api_key}"
            
            response = requests.get(geocode_url, timeout=10)
            
            if response.status_code != 200:
                return False, None, None, f"HTTP {response.status_code}"
            
            data = response.json()
            
            if data.get('status') != 'OK':
                return False, None, None, f"Status: {data.get('status')}"
            
            results = data.get('results', [])
            if not results:
                return False, None, None, "Không có kết quả"
            
            geometry = results[0].get('geometry', {})
            location = geometry.get('location', {})
            
            lat = location.get('lat')
            lng = location.get('lng')
            
            if lat is None or lng is None:
                return False, None, None, "Không có tọa độ"
            
            return True, lat, lng, None
            
        except requests.exceptions.Timeout:
            return False, None, None, "Hết thời gian chờ"
        except requests.exceptions.RequestException as e:
            return False, None, None, f"Lỗi yêu cầu: {str(e)}"
        except Exception as e:
            return False, None, None, f"Lỗi không xác định: {str(e)}"
    
    def _openmap_geocode_with_rate_limit(self, address):
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
        
        result = self._openmap_geocode_address(address)
        
        self.last_openmap_request_time = time.time()
        
        return result
    
    def _goong_geocode_address(self, address):
        """
        Call Goong.io Geocoding API to convert address to coordinates.
        
        Args:
            address: Full address string
            
        Returns:
            tuple: (success, latitude, longitude, error_message)
        """
        if not address or self.goong_api_key == "blank":
            return False, None, None, "Geocoding bị vô hiệu hóa"
        
        try:
            encoded_address = urllib.parse.quote(address)
            geocode_url = f"https://rsapi.goong.io/geocode?address={encoded_address}&api_key={self.goong_api_key}"
            
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
