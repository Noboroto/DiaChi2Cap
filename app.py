"""
Ứng dụng chuyển đổi địa chỉ 2 cấp
Giao diện GUI bằng tiếng Việt cho người dùng - CustomTkinter version
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests
import os
import threading
import time
from pathlib import Path
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

TEST_API_KEY = "testing-chuyen-doi-2-cap"
API_DOMAIN_PROD = "https://address-converter.io.vn"
API_DOMAIN_TEST = "http://localhost:5000"

MAX_BATCH_SIZE = 1000
BATCH_DELAY_SECONDS = 5

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")


class AddressConverterApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Chuyển đổi địa chỉ 2 cấp")
        self.root.geometry("800x750")
        
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.api_key_var = ctk.StringVar()
        self.input_file_path = ctk.StringVar()
        self.output_folder = ""
        self.is_converting = False
        self.api_key_visible = False
        
        self.account_info = {
            'name': '',
            'balance': 0,
            'createdAt': '',
            'updatedAt': ''
        }
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ctk.CTkFrame(self.root, corner_radius=15)
        main_frame.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        main_frame.grid_columnconfigure(1, weight=1)
        
        title_label = ctk.CTkLabel(
            main_frame,
            text="CHUYỂN ĐỔI ĐỊA CHỈ 2 CẤP",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(20, 30), padx=20)
        
        ctk.CTkLabel(
            main_frame,
            text="API Key:",
            font=ctk.CTkFont(size=13)
        ).grid(row=1, column=0, sticky="w", padx=20, pady=(10, 5))
        
        api_key_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        api_key_frame.grid(row=1, column=1, columnspan=2, sticky="ew", padx=20, pady=(10, 5))
        api_key_frame.grid_columnconfigure(0, weight=1)
        
        self.api_entry = ctk.CTkEntry(
            api_key_frame,
            textvariable=self.api_key_var,
            width=500,
            height=35,
            placeholder_text="Nhập API Key của bạn...",
            show="•"
        )
        self.api_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.api_entry.bind("<FocusOut>", lambda e: self.on_api_key_focus_out())
        self.api_entry.bind("<KeyRelease>", lambda e: self.auto_trim_api_key())
        
        self.toggle_api_btn = ctk.CTkButton(
            api_key_frame,
            text="Hiện",
            command=self.toggle_api_key_visibility,
            width=60,
            height=35,
            font=ctk.CTkFont(size=12)
        )
        self.toggle_api_btn.grid(row=0, column=1)
        
        self.account_info_frame = ctk.CTkFrame(
            main_frame,
            corner_radius=10,
            fg_color=("#e8f4f8", "#1a3a4a")
        )
        self.account_info_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 5))
        self.account_info_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self.account_name_label = ctk.CTkLabel(
            self.account_info_frame,
            text="Tài khoản: --",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.account_name_label.grid(row=0, column=0, sticky="w", padx=10, pady=8)
        
        self.account_balance_label = ctk.CTkLabel(
            self.account_info_frame,
            text="Số dư: --",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.account_balance_label.grid(row=0, column=1, sticky="w", padx=10, pady=8)
        
        self.account_created_label = ctk.CTkLabel(
            self.account_info_frame,
            text="Ngày tạo: --",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.account_created_label.grid(row=0, column=2, sticky="w", padx=10, pady=8)
        
        self.account_updated_label = ctk.CTkLabel(
            self.account_info_frame,
            text="Cập nhật: --",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )
        self.account_updated_label.grid(row=0, column=3, sticky="w", padx=10, pady=8)
        
        self.account_info_frame.grid_remove()
        
        ctk.CTkLabel(
            main_frame,
            text="File đầu vào:",
            font=ctk.CTkFont(size=13)
        ).grid(row=3, column=0, sticky="w", padx=20, pady=(10, 5))
        
        self.input_entry = ctk.CTkEntry(
            main_frame,
            textvariable=self.input_file_path,
            width=380,
            height=35,
            placeholder_text="Chọn file .txt hoặc .xlsx...",
            state="readonly"
        )
        self.input_entry.grid(row=3, column=1, sticky="ew", padx=(20, 10), pady=(10, 5))
        
        self.browse_btn = ctk.CTkButton(
            main_frame,
            text="Chọn file",
            command=self.browse_input_file,
            width=100,
            height=35,
            font=ctk.CTkFont(size=13)
        )
        self.browse_btn.grid(row=3, column=2, sticky="e", padx=20, pady=(10, 5))
        
        info_label = ctk.CTkLabel(
            main_frame,
            text="(Hỗ trợ file .xlsx và .txt)",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        info_label.grid(row=4, column=1, sticky="w", padx=20, pady=(0, 10))
        
        self.convert_btn = ctk.CTkButton(
            main_frame,
            text="CHUYỂN ĐỔI",
            command=self.start_conversion,
            width=200,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f6aa5", "#144870"),
            hover_color=("#144870", "#0d3147")
        )
        self.convert_btn.grid(row=5, column=0, columnspan=3, pady=20)
        
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator.grid(row=6, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(
            main_frame,
            text="Kết quả:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=7, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 10))
        
        self.result_textbox = ctk.CTkTextbox(
            main_frame,
            width=700,
            height=165,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.result_textbox.grid(row=8, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 10))
        self.result_textbox.configure(state="disabled")
        
        self.open_folder_btn = ctk.CTkButton(
            main_frame,
            text="Mở thư mục kết quả",
            command=self.open_output_folder,
            width=180,
            height=35,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.open_folder_btn.grid(row=9, column=0, columnspan=3, pady=(10, 10))
        
        self.progress_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("#1f6aa5", "#5fb4ff")
        )
        self.progress_label.grid(row=10, column=0, columnspan=3, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=700,
            height=15,
            corner_radius=8,
            mode="determinate"
        )
        self.progress_bar.grid(row=11, column=0, columnspan=3, padx=20, pady=(0, 20))
        self.progress_bar.set(0)
        
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file đầu vào",
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            
    def update_result_text(self, message, clear=False):
        self.result_textbox.configure(state="normal")
        if clear:
            self.result_textbox.delete("0.0", "end")
        self.result_textbox.insert("end", message + "\n")
        self.result_textbox.see("end")
        self.result_textbox.configure(state="disabled")
    
    def update_progress(self, current, total, status=""):
        if total > 0:
            percentage = (current / total) * 100
            self.progress_bar.set(percentage / 100)
            
            if status:
                label_text = f"{status} - {current}/{total} ({percentage:.1f}%)"
            else:
                label_text = f"{current}/{total} ({percentage:.1f}%)"
            
            self.progress_label.configure(text=label_text)
        else:
            self.progress_bar.set(0)
            self.progress_label.configure(text=status)

    def auto_trim_api_key(self):
        current_value = self.api_key_var.get()
        trimmed_value = current_value.strip()
        if current_value != trimmed_value:
            cursor_pos = self.api_entry.index("insert")
            self.api_key_var.set(trimmed_value)
            self.api_entry.icursor(max(0, cursor_pos - (len(current_value) - len(trimmed_value))))
        
    def start_conversion(self):
        if self.is_converting:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi!")
            return
            
        api_key = self.api_key_var.get().strip()
        input_file = self.input_file_path.get().strip()
        
        if not api_key:
            messagebox.showerror("Lỗi", "Vui lòng nhập API Key!")
            return
            
        if not input_file:
            messagebox.showerror("Lỗi", "Vui lòng chọn file đầu vào!")
            return
            
        if not os.path.exists(input_file):
            messagebox.showerror("Lỗi", "File không tồn tại!")
            return
            
        file_ext = Path(input_file).suffix.lower()
        if file_ext not in ['.txt', '.xlsx']:
            messagebox.showerror("Lỗi", "Chỉ hỗ trợ file .txt hoặc .xlsx!")
            return
        
        self.is_converting = True
        self.convert_btn.configure(state="disabled")
        self.open_folder_btn.configure(state="disabled")
        self.root.after(0, lambda: self.update_progress(0, 100, "Đang khởi tạo..."))
        
        thread = threading.Thread(target=self.perform_conversion, args=(api_key, input_file, file_ext))
        thread.daemon = True
        thread.start()
        
    def perform_conversion(self, api_key, input_file, file_ext):
        try:
            self.update_result_text("Đang đọc file đầu vào...", clear=True)
            self.root.after(0, lambda: self.update_progress(10, 100, "Đọc file đầu vào..."))
            
            if file_ext == '.txt':
                data, is_multi_column, headers = self.read_txt_file(input_file)
            else:
                data, is_multi_column, headers = self.read_excel_file(input_file)
            
            if not data:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "File đầu vào không có dữ liệu!"))
                return
            
            if is_multi_column:
                addresses = []
                original_data = data
                for row in data:
                    addr_parts = [
                        row.get('phuong_xa', ''),
                        row.get('quan_huyen', ''),
                        row.get('tinh_thanh', '')
                    ]
                    address = ', '.join([p for p in addr_parts if p])
                    addresses.append(address)
                
                self.update_result_text(f"[ĐỊA CHỈ NHIỀU CỘT] Đã phát hiện định dạng {len(headers)} cột")
                self.update_result_text(f"Sử dụng pattern: Phường Xã, Quận Huyện, Tỉnh Thành")
            else:
                addresses = data
                original_data = None
                self.update_result_text(f"[ĐỊA CHỈ ĐƠN] Đã phát hiện định dạng 1 cột")
                
            total_addresses = len(addresses)
            self.update_result_text(f"Đã đọc {total_addresses} địa chỉ từ file")
            self.root.after(0, lambda: self.update_progress(20, 100, "Chuẩn bị xử lý..."))
            
            num_batches = (total_addresses + MAX_BATCH_SIZE - 1) // MAX_BATCH_SIZE
            
            if num_batches > 1:
                self.update_result_text(f"\n[CẢNH BÁO] File có {total_addresses} địa chỉ, vượt quá giới hạn {MAX_BATCH_SIZE} địa chỉ/lần")
                self.update_result_text(f"Hệ thống sẽ tự động chia thành {num_batches} lần gửi")
                self.update_result_text(f"Thời gian chờ giữa các lần: {BATCH_DELAY_SECONDS} giây\n")
            
            api_domain = API_DOMAIN_TEST if api_key == TEST_API_KEY else API_DOMAIN_PROD
            convert_endpoint = f"{api_domain}/api/convert-batch"

            results_dict = {}
            total_successful = 0
            total_failed = 0
            skipped_indices = set()
            
            for batch_num in range(num_batches):
                start_idx = batch_num * MAX_BATCH_SIZE
                end_idx = min((batch_num + 1) * MAX_BATCH_SIZE, total_addresses)
                
                batch_items = [(i, addresses[i]) for i in range(start_idx, end_idx) if i not in skipped_indices]
                
                batch_info = f"Lần {batch_num + 1}/{num_batches}" if num_batches > 1 else ""
                if batch_info:
                    self.update_result_text(f"{batch_info}: Xử lý địa chỉ {start_idx + 1} đến {end_idx}")
                
                retry_count = 0
                max_retries = 100
                
                while retry_count < max_retries and batch_items:
                    progress_start = 20 + (batch_num * 70 // num_batches)
                    retry_info = f" (Retry {retry_count})" if retry_count > 0 else ""
                    self.root.after(0, lambda p=progress_start, b=batch_info, r=retry_info: self.update_progress(
                        p, 100, f"Đang gửi yêu cầu {b}{r}..." if b else f"Đang gửi yêu cầu{r}..."
                    ))
                    
                    batch_addresses = [addr for idx, addr in batch_items]
                    
                    response = requests.post(
                        convert_endpoint,
                        json={
                            "addresses": batch_addresses,
                            "key": api_key
                        },
                        headers={"Content-Type": "application/json"},
                        timeout=60
                    )
                    
                    result_data = response.json()
                    
                    if not result_data.get("success", False):
                        error_msg = result_data.get("error", "Lỗi không xác định")
                        
                        if result_data.get("rateLimited", False):
                            retry_after = result_data.get("retryAfter", 0)
                            self.update_result_text(f"\n[RATE LIMIT] {error_msg}")
                            self.update_result_text(f"Tự động thử lại sau {retry_after} giây...")
                            
                            for i in range(retry_after):
                                time.sleep(1)
                                remaining = retry_after - i - 1
                                if remaining > 0:
                                    self.root.after(0, lambda r=remaining: self.progress_label.configure(
                                        text=f"Rate limited - Chờ {r} giây..."
                                    ))
                            continue
                        else:
                            self.update_result_text(f"\n[LỖI] {error_msg}")
                            self.root.after(0, lambda e=error_msg: messagebox.showerror("Lỗi API", e))
                            return
                    
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
                                total_failed += 1
                        else:
                            results_dict[original_idx] = result
                            total_successful += 1
                    
                    if balance_error_indices:
                        skipped_indices.update(balance_error_indices)
                        
                        duplicates_in_remaining = 0
                        for idx, addr in batch_items:
                            if idx not in balance_error_indices and addr in balance_error_addrs:
                                skipped_indices.add(idx)
                                results_dict[idx] = {
                                    "original": addr,
                                    "converted": "",
                                    "error": "Số dư không đủ - Đã bỏ qua (trùng)",
                                    "success": False
                                }
                                duplicates_in_remaining += 1
                        
                        total_skipped = len(balance_error_indices)
                        self.update_result_text(f"\n[SỐ DƯ KHÔNG ĐỦ] Bỏ qua {total_skipped} địa chỉ")
                        if duplicates_in_remaining > 0:
                            self.update_result_text(f"  + Bỏ qua thêm {duplicates_in_remaining} địa chỉ trùng")
                        
                        batch_items = [(idx, addr) for idx, addr in batch_items if idx not in skipped_indices]
                        
                        if batch_items:
                            self.update_result_text(f"Còn lại {len(batch_items)} địa chỉ, tiếp tục xử lý...")
                            retry_count += 1
                            time.sleep(1)
                            continue
                        else:
                            self.update_result_text("Tất cả địa chỉ trong batch đã được xử lý")
                            break
                    
                    break
                
                if retry_count >= max_retries:
                    self.update_result_text(f"\n[CẢNH BÁO] Đã vượt quá số lần retry tối đa ({max_retries})")
                
                if batch_num < num_batches - 1:
                    self.update_result_text(f"Chờ {BATCH_DELAY_SECONDS} giây trước khi gửi lần tiếp theo...")
                    for i in range(BATCH_DELAY_SECONDS):
                        time.sleep(1)
                        remaining = BATCH_DELAY_SECONDS - i - 1
                        if remaining > 0:
                            self.root.after(0, lambda r=remaining: self.progress_label.configure(
                                text=f"Chờ {r} giây..."
                            ))
            
            all_results = [results_dict[i] for i in range(total_addresses)]
            
            self.root.after(0, lambda: self.update_progress(90, 100, "Đang lưu kết quả..."))

            total_skipped = len(skipped_indices)
            
            self.update_result_text(f"\n{'='*50}")
            self.update_result_text(f"TỔNG KẾT:")
            self.update_result_text(f"  - Tổng số địa chỉ: {total_addresses}")
            self.update_result_text(f"  - Thành công: {total_successful}")
            self.update_result_text(f"  - Thất bại: {total_failed}")
            if total_skipped > 0:
                self.update_result_text(f"  - Bỏ qua (Số dư không đủ): {total_skipped}")
            if num_batches > 1:
                self.update_result_text(f"  - Số lần gửi: {num_batches}")
            self.update_result_text(f"{'='*50}\n")
            
            input_path = Path(input_file)
            output_folder = input_path.parent / "output"
            output_folder.mkdir(exist_ok=True)
            self.output_folder = str(output_folder)
            
            output_filename = f"{input_path.stem}_converted{file_ext}"
            output_path = output_folder / output_filename
            
            if file_ext == '.txt':
                self.write_txt_output(output_path, all_results, is_multi_column, headers, original_data)
            else:
                self.write_excel_output(output_path, all_results, is_multi_column, headers, original_data)
            
            self.update_result_text(f"Đã lưu kết quả tại:\n{output_path}")
            self.root.after(0, lambda: self.update_progress(100, 100, "Hoàn thành!"))
            
            self.root.after(0, lambda: self.open_folder_btn.configure(state="normal"))
            self.root.after(0, lambda s=total_successful, f=total_failed, sk=total_skipped, fn=output_filename: messagebox.showinfo(
                "Hoàn thành", 
                f"Chuyển đổi thành công!\n\nThành công: {s}\nThất bại: {f}\nBỏ qua: {sk}\n\nFile kết quả: {fn}"
            ))
            
        except requests.exceptions.Timeout:
            self.update_result_text("\n[LỖI] Timeout - Không thể kết nối đến API")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến API (Timeout)"))
        except requests.exceptions.ConnectionError:
            self.update_result_text("\n[LỖI] Không thể kết nối đến server")
            if api_key == TEST_API_KEY:
                self.update_result_text("Hãy chắc chắn test server đang chạy tại http://localhost:5000")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến server"))
        except Exception as e:
            self.update_result_text(f"\n[LỖI] {str(e)}")
            self.root.after(0, lambda e=str(e): messagebox.showerror("Lỗi", f"Lỗi xử lý: {e}"))
        finally:
            self.is_converting = False
            self.root.after(0, lambda: self.convert_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
            
    def read_txt_file(self, file_path):
        """Read txt file and detect format: single column or multi-column (5+ columns)
        
        Returns:
            tuple: (addresses_or_rows, is_multi_column, headers)
            - addresses_or_rows: list of strings (single column) or list of dicts (multi-column)
            - is_multi_column: boolean indicating format type
            - headers: list of header names (for multi-column) or None
        """
        data = []
        is_multi_column = False
        headers = None
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
            
            if not lines:
                return [], False, None
            
            first_line_parts = [p.strip() for p in lines[0].split(',')]
            
            if len(first_line_parts) >= 5:
                is_multi_column = True
                headers = first_line_parts
                
                for line in lines[1:]:
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        row_data = {
                            'code': parts[0],
                            'so_nha_duong': parts[1],
                            'phuong_xa': parts[2],
                            'quan_huyen': parts[3],
                            'tinh_thanh': parts[4],
                            'extra_columns': parts[5:] if len(parts) > 5 else []
                        }
                        data.append(row_data)
            else:
                for line in lines:
                    if line:
                        data.append(line)
        
        except Exception as e:
            self.update_result_text(f"[LỖI] Không thể đọc file txt: {str(e)}")
            return [], False, None
        
        return data, is_multi_column, headers
        
    def read_excel_file(self, file_path):
        """Read Excel file and detect format: single column or multi-column (5+ columns)
        
        Returns:
            tuple: (addresses_or_rows, is_multi_column, headers)
            - addresses_or_rows: list of strings (single column) or list of dicts (multi-column)
            - is_multi_column: boolean indicating format type
            - headers: list of header names (for multi-column) or None
        """
        data = []
        is_multi_column = False
        headers = None
        
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            
            rows = list(ws.iter_rows(values_only=True))
            wb.close()
            
            if not rows:
                return [], False, None
            
            first_row = rows[0]
            num_cols = sum(1 for cell in first_row if cell is not None and str(cell).strip())
            
            if num_cols >= 5:
                is_multi_column = True
                headers = [str(cell).strip() if cell is not None else '' for cell in first_row]
                
                for row in rows[1:]:
                    if row and any(cell is not None for cell in row):
                        cells = [str(cell).strip() if cell is not None else '' for cell in row]
                        if len(cells) >= 5 and any(cells[:5]):
                            row_data = {
                                'code': cells[0] if len(cells) > 0 else '',
                                'so_nha_duong': cells[1] if len(cells) > 1 else '',
                                'phuong_xa': cells[2] if len(cells) > 2 else '',
                                'quan_huyen': cells[3] if len(cells) > 3 else '',
                                'tinh_thanh': cells[4] if len(cells) > 4 else '',
                                'extra_columns': cells[5:] if len(cells) > 5 else []
                            }
                            data.append(row_data)
            else:
                for row in rows:
                    if row and row[0]:
                        addr = str(row[0]).strip()
                        if addr:
                            data.append(addr)
        
        except Exception as e:
            self.update_result_text(f"[LỖI] Không thể đọc file Excel: {str(e)}")
            return [], False, None
        
        return data, is_multi_column, headers
        
    def write_txt_output(self, output_path, results, is_multi_column=False, headers=None, original_data=None):
        """Write output to txt file
        
        Args:
            output_path: Path to output file
            results: List of conversion results
            is_multi_column: Boolean indicating if multi-column format
            headers: List of header names (for multi-column)
            original_data: List of original row dicts (for multi-column)
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if is_multi_column and headers and original_data:
                    new_headers = headers + ['Chuyển đổi']
                    f.write(','.join(new_headers) + '\n')
                    
                    for idx, result in enumerate(results):
                        if idx < len(original_data):
                            row_data = original_data[idx]
                            row_parts = [
                                row_data.get('code', ''),
                                row_data.get('so_nha_duong', ''),
                                row_data.get('phuong_xa', ''),
                                row_data.get('quan_huyen', ''),
                                row_data.get('tinh_thanh', '')
                            ]
                            row_parts.extend(row_data.get('extra_columns', []))
                            
                            if result.get("success", False):
                                converted = result.get("converted", "")
                            else:
                                error_msg = result.get("error", "Lỗi không xác định")
                                converted = f"LỖI: {error_msg}"
                            
                            row_parts.append(converted)
                            f.write(','.join(row_parts) + '\n')
                else:
                    for result in results:
                        if result.get("success", False):
                            f.write(result.get("converted", "") + "\n")
                        else:
                            error_msg = result.get("error", "Lỗi không xác định")
                            f.write(f"LỖI: {error_msg}\n")
        except Exception as e:
            self.update_result_text(f"[LỖI] Không thể ghi file txt: {str(e)}")
            
    def write_excel_output(self, output_path, results, is_multi_column=False, headers=None, original_data=None):
        """Write output to Excel file
        
        Args:
            output_path: Path to output file
            results: List of conversion results
            is_multi_column: Boolean indicating if multi-column format
            headers: List of header names (for multi-column)
            original_data: List of original row dicts (for multi-column)
        """
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Kết quả"
            
            header_font = Font(bold=True, size=11)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
            if is_multi_column and headers and original_data:
                new_headers = headers + ['Chuyển đổi']
                
                for col_idx, header in enumerate(new_headers, start=1):
                    cell = ws.cell(row=1, column=col_idx, value=header)
                    cell.font = header_font
                    cell.fill = header_fill
                    cell.alignment = header_alignment
                
                for idx, result in enumerate(results, start=2):
                    orig_idx = idx - 2
                    if orig_idx < len(original_data):
                        row_data = original_data[orig_idx]
                        
                        ws.cell(row=idx, column=1, value=row_data.get('code', ''))
                        ws.cell(row=idx, column=2, value=row_data.get('so_nha_duong', ''))
                        ws.cell(row=idx, column=3, value=row_data.get('phuong_xa', ''))
                        ws.cell(row=idx, column=4, value=row_data.get('quan_huyen', ''))
                        ws.cell(row=idx, column=5, value=row_data.get('tinh_thanh', ''))
                        
                        extra_cols = row_data.get('extra_columns', [])
                        for extra_idx, extra_val in enumerate(extra_cols):
                            ws.cell(row=idx, column=6+extra_idx, value=extra_val)
                        
                        conversion_col = 6 + len(extra_cols)
                        if result.get("success", False):
                            ws.cell(row=idx, column=conversion_col, value=result.get("converted", ""))
                        else:
                            error_msg = result.get("error", "Lỗi không xác định")
                            cell = ws.cell(row=idx, column=conversion_col, value=f"LỖI: {error_msg}")
                            cell.font = Font(color="FF0000")
                
                for col_idx in range(1, len(new_headers) + 1):
                    ws.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = 20
            else:
                ws['A1'] = "Gốc"
                ws['B1'] = "Chuyển đổi"
                
                ws['A1'].font = header_font
                ws['B1'].font = header_font
                ws['A1'].fill = header_fill
                ws['B1'].fill = header_fill
                ws['A1'].alignment = header_alignment
                ws['B1'].alignment = header_alignment
                
                ws.column_dimensions['A'].width = 50
                ws.column_dimensions['B'].width = 60
                
                for idx, result in enumerate(results, start=2):
                    ws[f'A{idx}'] = result.get("original", "")
                    if result.get("success", False):
                        ws[f'B{idx}'] = result.get("converted", "")
                    else:
                        error_msg = result.get("error", "Lỗi không xác định")
                        ws[f'B{idx}'] = f"LỖI: {error_msg}"
                        ws[f'B{idx}'].font = Font(color="FF0000")
            
            wb.save(output_path)
            wb.close()
        except Exception as e:
            self.update_result_text(f"[LỖI] Không thể ghi file Excel: {str(e)}")
            
    def open_output_folder(self):
        if self.output_folder and os.path.exists(self.output_folder):
            os.startfile(self.output_folder)
        else:
            messagebox.showerror("Lỗi", "Thư mục kết quả không tồn tại!")

    def on_api_key_focus_out(self):
        api_key = self.api_key_var.get().strip()
        if api_key:
            thread = threading.Thread(target=self.fetch_account_info, args=(api_key,))
            thread.daemon = True
            thread.start()
        else:
            self.root.after(0, lambda: self.account_info_frame.grid_remove())
    
    def fetch_account_info(self, api_key):
        try:
            api_domain = API_DOMAIN_TEST if api_key == TEST_API_KEY else API_DOMAIN_PROD
            account_status_endpoint = f"{api_domain}/api/account-status"
            
            response = requests.get(f"{account_status_endpoint}?key={api_key}", timeout=10)
            data = response.json()
            if response.status_code == 200:
                if data.get('success'):
                    account_data = data.get('data', {})
                    self.account_info['status'] = 'hoạt động'
                    self.account_info['balance'] = account_data.get('balance', 0)
                    self.account_info['createdAt'] = account_data.get('createdAt', '-')
                    self.account_info['updatedAt'] = account_data.get('updatedAt', '-')
                    
                    self.root.after(0, self.update_account_info_display)
                else:
                    self.account_info['status'] = data.get('error', 'không xác định')
                    self.account_info['balance'] = -1
                    self.account_info['createdAt'] = "-"
                    self.account_info['updatedAt'] = "-"
                self.root.after(0, self.update_account_info_display)
            else:
                self.account_info['status'] = data.get('error', 'không xác định')
                self.account_info['balance'] = -1
                self.account_info['createdAt'] = "-"
                self.account_info['updatedAt'] = "-"
                self.root.after(0, self.update_account_info_display)
        except Exception as e:
            self.account_info['status'] = f"không xác định: ({str(e)})"
            self.account_info['balance'] = -1
            self.account_info['createdAt'] = "-"
            self.account_info['updatedAt'] = "-"
            self.root.after(0, self.update_account_info_display)
    
    def update_account_info_display(self):
        from datetime import datetime
        
        self.account_name_label.configure(
            text=f"Tình trạng: {self.account_info['status']}"
        )
        
        balance_formatted = f"{self.account_info['balance']:,}đ".replace(',', '.')
        self.account_balance_label.configure(
            text=f"Số dư: {balance_formatted}"
        )
        
        try:
            created_dt = datetime.fromisoformat(self.account_info['createdAt'].replace('Z', '+00:00'))
            created_str = created_dt.strftime('%d/%m/%Y')
        except Exception:
            created_str = '--'
        
        self.account_created_label.configure(
            text=f"Ngày tạo: {created_str}"
        )
        
        try:
            updated_dt = datetime.fromisoformat(self.account_info['updatedAt'].replace('Z', '+00:00'))
            updated_str = updated_dt.strftime('%d/%m/%Y %H:%M')
        except Exception:
            updated_str = '--'
        
        self.account_updated_label.configure(
            text=f"Cập nhật: {updated_str}"
        )
        
        self.account_info_frame.grid()

    def toggle_api_key_visibility(self):
        self.api_key_visible = not self.api_key_visible
        
        if self.api_key_visible:
            self.api_entry.configure(show="")
            self.toggle_api_btn.configure(text="Ẩn")
        else:
            self.api_entry.configure(show="•")
            self.toggle_api_btn.configure(text="Hiện")


def main():
    app = AddressConverterApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
