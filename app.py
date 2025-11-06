# -*- coding: utf-8 -*-
"""
Ứng dụng chuyển đổi địa chỉ 2 cấp
Giao diện GUI bằng tiếng Việt cho người dùng - CustomTkinter version (Modular)
"""
import customtkinter as ctk
from tkinter import filedialog, messagebox
import requests
import os
import threading
import time
from pathlib import Path

from modules.utils import (
    TEST_API_KEY,
    API_DOMAIN_PROD,
    API_DOMAIN_TEST,
    GOONG_API_KEY,
    OPENMAP_API_KEY,
    MAX_ADDRESS_BATCH_SIZE,
    BATCH_DELAY_SECONDS,
    OPENMAP_RATE_LIMIT_DELAY
)

from modules.api_client import AddressAPIClient
from modules.conversion_processor import ConversionProcessor
from modules.file_handlers import (
    read_txt_file,
    read_excel_file,
    write_txt_output,
    write_excel_output
)

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
        
        self.processor = None
        
        self.account_info = {
            'status': '',
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
            text="Tình trạng: --",
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
        
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=5, column=0, columnspan=3, pady=20)
        
        self.convert_btn = ctk.CTkButton(
            button_frame,
            text="CHUYỂN ĐỔI",
            command=self.start_conversion,
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#1f6aa5", "#144870"),
            hover_color=("#144870", "#0d3147")
        )
        self.convert_btn.grid(row=0, column=1, padx=10)
        
        self.stop_btn = ctk.CTkButton(
            button_frame,
            text="DỪNG",
            command=self.stop_conversion,
            width=180,
            height=45,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color=("#d32f2f", "#b71c1c"),
            hover_color=("#b71c1c", "#8b0000"),
            state="disabled"
        )
        self.stop_btn.grid(row=0, column=0, padx=10)
        
        self.open_folder_btn = ctk.CTkButton(
            button_frame,
            text="MỞ THƯ MỤC KẾT QUẢ",
            command=self.open_output_folder,
            width=180,
            height=45,
            font=ctk.CTkFont(size=13),
            state="disabled"
        )
        self.open_folder_btn.grid(row=0, column=2, padx=10)
        
        separator = ctk.CTkFrame(main_frame, height=2, fg_color="gray30")
        separator.grid(row=6, column=0, columnspan=3, sticky="ew", padx=20, pady=(10, 20))
        
        self.progress_label = ctk.CTkLabel(
            main_frame,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=("#1f6aa5", "#5fb4ff")
        )
        self.progress_label.grid(row=7, column=0, columnspan=3, pady=(10, 5))
        
        self.progress_bar = ctk.CTkProgressBar(
            main_frame,
            width=700,
            height=15,
            corner_radius=8,
            mode="determinate"
        )
        self.progress_bar.grid(row=8, column=0, columnspan=3, padx=20, pady=(0, 20))
        self.progress_bar.set(0)
        
        ctk.CTkLabel(
            main_frame,
            text="Kết quả:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=9, column=0, columnspan=3, sticky="w", padx=20, pady=(10, 10))
        
        self.result_textbox = ctk.CTkTextbox(
            main_frame,
            width=700,
            height=165,
            font=ctk.CTkFont(family="Consolas", size=11),
            wrap="word"
        )
        self.result_textbox.grid(row=10, column=0, columnspan=3, sticky="ew", padx=20, pady=(0, 10))
        self.result_textbox.configure(state="disabled")
        
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
            self.update_result_text(f"Đã chọn file: {os.path.basename(file_path)}", clear=True)
            
    def update_result_text(self, message, clear=False):
        self.result_textbox.configure(state="normal")
        if clear:
            self.result_textbox.delete("1.0", "end")
        self.result_textbox.insert("end", message + "\n")
        self.result_textbox.see("end")
        self.result_textbox.configure(state="disabled")
    
    def update_progress(self, current, total, status=""):
        if total > 0:
            progress = current / total
            self.progress_bar.set(progress)
            if status:
                self.progress_label.configure(text=status)
        else:
            self.progress_bar.set(0)
            if status:
                self.progress_label.configure(text=status)

    def auto_trim_api_key(self):
        current_value = self.api_key_var.get()
        trimmed_value = current_value.strip()
        if current_value != trimmed_value:
            self.api_key_var.set(trimmed_value)

    def start_conversion(self):
        if self.is_converting:
            messagebox.showwarning("Cảnh báo", "Đang trong quá trình chuyển đổi!")
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
            messagebox.showerror("Lỗi", "File đầu vào không tồn tại!")
            return
            
        file_ext = Path(input_file).suffix.lower()
        if file_ext not in ['.txt', '.xlsx']:
            messagebox.showerror("Lỗi", "Chỉ hỗ trợ file .txt và .xlsx!")
            return
        
        self.is_converting = True
        self.convert_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.open_folder_btn.configure(state="disabled")
        self.root.after(0, lambda: self.update_progress(0, 100, "Đang khởi tạo..."))
        
        thread = threading.Thread(target=self.perform_conversion, args=(api_key, input_file, file_ext))
        thread.daemon = True
        thread.start()

    def stop_conversion(self):
        """Request to stop the conversion process"""
        if self.is_converting and self.processor:
            self.processor.request_stop()
            self.update_result_text("\n[DỪNG] Đang dừng quá trình chuyển đổi...")
            self.update_result_text("Sẽ lưu kết quả đã xử lý...")
            self.root.after(0, lambda: self.progress_label.configure(text="Đang dừng và lưu kết quả..."))
            self.stop_btn.configure(state="disabled")

    def perform_conversion(self, api_key, input_file, file_ext):
        try:
            conversion_start_time = time.time()
            
            self.update_result_text("Đang đọc file đầu vào...", clear=True)
            self.root.after(0, lambda: self.update_progress(10, 100, "Đọc file đầu vào..."))
            
            if file_ext == '.txt':
                data, is_multi_column, headers = read_txt_file(input_file)
            else:
                data, is_multi_column, headers = read_excel_file(input_file)
            
            if not data:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "File đầu vào không có dữ liệu!"))
                return
            
            api_domain = API_DOMAIN_TEST if api_key == TEST_API_KEY else API_DOMAIN_PROD
            api_client = AddressAPIClient(api_key, api_domain, MAX_ADDRESS_BATCH_SIZE, BATCH_DELAY_SECONDS)
            
            self.processor = ConversionProcessor(
                api_client,
                GOONG_API_KEY,
                OPENMAP_API_KEY,
                OPENMAP_RATE_LIMIT_DELAY,
                progress_callback=lambda msg: self.root.after(0, lambda m=msg: self.update_result_text(m))
            )
            self.processor.reset_stop_flag()
            
            self.update_result_text(f"\n{'='*50}")
            self.update_result_text("[BƯỚC 1] CHUẨN BỊ DỮ LIỆU")
            self.update_result_text(f"{'='*50}")
            
            addresses_with_street, addresses_no_street, original_data, pre_converted_indices = self.processor.prepare_addresses(data, is_multi_column)
            
            total_addresses = len(addresses_with_street)
            
            if is_multi_column:
                num_headers = len(headers) if headers else 0
                self.update_result_text(f"[ĐỊA CHỈ NHIỀU CỘT] Đã phát hiện định dạng {num_headers} cột")
            else:
                self.update_result_text(f"[ĐỊA CHỈ ĐƠN] Đã phát hiện định dạng 1 cột")
            
            if pre_converted_indices:
                self.update_result_text(f"[PRE] Đã áp dụng chuyển đổi có sẵn cho {len(pre_converted_indices)} địa chỉ")
            
            self.update_result_text(f"Đã đọc {total_addresses} địa chỉ từ file")
            self.root.after(0, lambda: self.update_progress(20, 100, "Chuẩn bị xử lý..."))
            
            results_dict = {}
            skipped_indices = set()
            
            for idx in range(total_addresses):
                results_dict[idx] = {
                    "original": addresses_with_street[idx],
                    "converted": "",
                    "success": False,
                    "retryCount": 0
                }
            
            for idx, converted_addr in pre_converted_indices.items():
                results_dict[idx] = {
                    "original": addresses_with_street[idx],
                    "converted": converted_addr,
                    "success": True,
                    "preConverted": True,
                    "retryCount": 1
                }
                skipped_indices.add(idx)
            
            cumulative_success = len(skipped_indices)
            
            if self.processor.stop_requested:
                self.update_result_text("\n[DỪNG] Đã dừng sau bước 2.1")
                failed_indices_set = set()
            else:
                self.update_result_text(f"\n{'='*50}")
                self.update_result_text("[BƯỚC 2] XỬ LÝ ĐỊA CHỈ CHI TIẾT")
                self.update_result_text(f"{'='*50}")
                self.root.after(0, lambda: self.update_progress(30, 100, "Bước 2..."))
                
                batch_results, successful, failed, failed_indices_set = self.processor.process_single_parallel(
                    addresses_with_street, skipped_indices
                )
                
                results_dict.update(batch_results)
                cumulative_success += successful
                self.update_result_text(f"Bước này: {successful} thành công, {failed} thất bại")
                self.update_result_text(f"Tổng lũy kế: {cumulative_success} thành công, {total_addresses - cumulative_success} còn lại")
            
            if not self.processor.stop_requested and failed_indices_set:
                self.update_result_text(f"\n{'='*50}")
                self.update_result_text("[BƯỚC 3] XỬ LÝ ĐIA CHỈ BỊ LỖI, CHỈ GIỮ 3 CẤP CƠ BẢN")
                self.update_result_text(f"{'='*50}")
                self.root.after(0, lambda: self.update_progress(50, 100, "Bước 3..."))
                
                batch_results_2_3, step_2_3_success, step_2_3_failed, failed_indices_set = self.processor.process_batch_retry(
                    addresses_no_street, results_dict, failed_indices_set
                )
                
                results_dict.update(batch_results_2_3)
                cumulative_success += step_2_3_success
                self.update_result_text(f"Bước này: {step_2_3_success} thành công, {step_2_3_failed} thất bại")
                self.update_result_text(f"Tổng lũy kế: {cumulative_success} thành công, {total_addresses - cumulative_success} còn lại")
            
            if not self.processor.stop_requested and (GOONG_API_KEY != "blank" or OPENMAP_API_KEY != "blank"):
                if failed_indices_set:
                    self.update_result_text(f"\n{'='*50}")
                    self.update_result_text("[BƯỚC 4-6] Tìm kiếm tọa độ để chuyển đổi")
                    self.update_result_text(f"{'='*50}")
                    self.root.after(0, lambda: self.update_progress(70, 100, "Đang tìm tọa độ..."))
                    
                    results_dict, geocoded_success = self.processor.geocode_fallback_openmap_goong(
                        addresses_with_street, addresses_no_street, results_dict, failed_indices_set
                    )
                    
                    if geocoded_success > 0:
                        cumulative_success += geocoded_success
                        self.update_result_text(f"Bước này: {geocoded_success} thành công")
                        self.update_result_text(f"Tổng lũy kế: {cumulative_success} thành công, {total_addresses - cumulative_success} còn lại")
            
            if self.processor.stop_requested:
                for i in range(total_addresses):
                    if not results_dict[i].get("success", False) and results_dict[i].get("retryCount", 0) == 0:
                        results_dict[i]["error"] = "Chưa xử lý (đã dừng)"
            
            all_results = [results_dict[i] for i in range(total_addresses)]
            
            if self.processor.stop_requested:
                self.root.after(0, lambda: self.update_progress(90, 100, "Đã dừng - Đang lưu kết quả..."))
            else:
                self.root.after(0, lambda: self.update_progress(90, 100, "Đang lưu kết quả..."))

            actual_successful = sum(1 for r in all_results if r.get("success", False))
            actual_failed = sum(1 for r in all_results if not r.get("success", False) and "Chưa xử lý" not in r.get("error", ""))
            total_skipped = len(skipped_indices)
            total_not_processed = sum(1 for r in all_results if not r.get("success", False) and "Chưa xử lý" in r.get("error", ""))
            
            conversion_elapsed = time.time() - conversion_start_time
            
            self.update_result_text(f"\n{'='*50}")
            if self.processor.stop_requested:
                self.update_result_text("ĐÃ DỪNG - TỔNG KẾT:")
            else:
                self.update_result_text("TỔNG KẾT:")
            self.update_result_text(f"\t- Tổng số địa chỉ: {total_addresses}")
            self.update_result_text(f"\t- Thành công: {actual_successful}")
            self.update_result_text(f"\t- Thất bại: {actual_failed}")
            if total_not_processed > 0:
                self.update_result_text(f"\t- Chưa xử lý: {total_not_processed}")
            self.update_result_text(f"\t- Tổng thời gian: {conversion_elapsed:.3f}s")
            self.update_result_text(f"{'='*50}\n")
            
            input_path = Path(input_file)
            output_folder = input_path.parent / "output"
            output_folder.mkdir(exist_ok=True)
            self.output_folder = str(output_folder)
            
            output_filename = f"{input_path.stem}_converted{file_ext}"
            output_path = output_folder / output_filename
            
            if self.processor.stop_requested:
                self.root.after(0, lambda: self.update_progress(95, 100, "Đã dừng - Đang ghi file..."))
            else:
                self.root.after(0, lambda: self.update_progress(95, 100, "Đang ghi file..."))
            
            if file_ext == '.txt':
                write_txt_output(output_path, all_results, is_multi_column, headers, original_data)
            else:
                write_excel_output(output_path, all_results, is_multi_column, headers, original_data)
            
            self.update_result_text(f"Đã lưu kết quả tại:\n{output_path}")
            if self.processor.stop_requested:
                self.root.after(0, lambda: self.update_progress(100, 100, "Đã dừng - Đã lưu kết quả!"))
            else:
                self.root.after(0, lambda: self.update_progress(100, 100, "Hoàn thành!"))
            
            self.root.after(0, lambda: self.open_folder_btn.configure(state="normal"))
            
            if self.processor.stop_requested:
                self.root.after(0, lambda s=actual_successful, f=actual_failed, sk=total_skipped, np=total_not_processed, fn=output_filename: messagebox.showinfo(
                    "Đã dừng", 
                    f"Đã dừng và lưu kết quả!\n\nThành công: {s}\nThất bại: {f}\nChưa xử lý: {np}\n\nFile kết quả: {fn}"
                ))
            else:
                self.root.after(0, lambda s=actual_successful, f=actual_failed, sk=total_skipped, fn=output_filename: messagebox.showinfo(
                    "Hoàn thành", 
                    f"Chuyển đổi thành công!\n\nThành công: {s}\nThất bại: {f}\n\nFile kết quả: {fn}"
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
            self.processor = None
            self.root.after(0, lambda: self.convert_btn.configure(state="normal"))
            self.root.after(0, lambda: self.stop_btn.configure(state="disabled"))
            self.root.after(0, lambda: self.progress_label.configure(text=""))
            
    def open_output_folder(self):
        if self.output_folder and os.path.exists(self.output_folder):
            os.startfile(self.output_folder)

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
            api_client = AddressAPIClient(api_key, api_domain)
            
            account_data = api_client.fetch_account_info()
            
            if account_data:
                self.account_info['status'] = 'hoạt động'
                self.account_info['balance'] = account_data.get('balance', 0)
                self.account_info['createdAt'] = account_data.get('createdAt', '-')
                self.account_info['updatedAt'] = account_data.get('updatedAt', '-')
                
                self.root.after(0, self.update_account_info_display)
            else:
                self.account_info['status'] = 'không xác định'
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
        if self.api_key_visible:
            self.api_entry.configure(show="•")
            self.toggle_api_btn.configure(text="Hiện")
            self.api_key_visible = False
        else:
            self.api_entry.configure(show="")
            self.toggle_api_btn.configure(text="Ẩn")
            self.api_key_visible = True


def main():
    app = AddressConverterApp()
    app.root.mainloop()


if __name__ == "__main__":
    main()
