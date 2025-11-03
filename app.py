"""
Ứng dụng chuyển đổi địa chỉ 2 cấp
Giao diện GUI bằng tiếng Việt cho người dùng
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
import os
import threading
import time
from pathlib import Path
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill

TEST_API_KEY = "testing-chuyen-doi-2-cap"
API_ENDPOINT_PROD = "https://address-converter.io.vn/api/convert-batch"
API_ENDPOINT_TEST = "http://localhost:5000/api/convert-batch"

MAX_BATCH_SIZE = 1000
BATCH_DELAY_SECONDS = 5


class AddressConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chuyển đổi địa chỉ 2 cấp")
        self.root.geometry("700x500")
        self.root.resizable(False, False)
        
        self.api_key = tk.StringVar()
        self.input_file_path = tk.StringVar()
        self.output_folder = ""
        self.is_converting = False
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        title_label = ttk.Label(
            main_frame, 
            text="CHUYỂN ĐỔI ĐỊA CHỈ 2 CẤP",
            font=("Segoe UI", 16, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        ttk.Label(main_frame, text="API Key:", font=("Segoe UI", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        api_entry = ttk.Entry(main_frame, textvariable=self.api_key, width=50, show="*")
        api_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(main_frame, text="File đầu vào:", font=("Segoe UI", 10)).grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        input_entry = ttk.Entry(main_frame, textvariable=self.input_file_path, width=40, state="readonly")
        input_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)
        
        browse_btn = ttk.Button(main_frame, text="Chọn file", command=self.browse_input_file)
        browse_btn.grid(row=2, column=2, padx=(5, 0), pady=5)
        
        ttk.Label(
            main_frame, 
            text="(Chỉ hỗ trợ file .txt hoặc .xlsx)", 
            font=("Segoe UI", 8),
            foreground="gray"
        ).grid(row=3, column=1, sticky=tk.W, pady=(0, 10))
        
        self.convert_btn = ttk.Button(
            main_frame, 
            text="CHUYỂN ĐỔI", 
            command=self.start_conversion,
            style="Accent.TButton"
        )
        self.convert_btn.grid(row=4, column=0, columnspan=3, pady=15, ipadx=40, ipady=10)
        
        separator = ttk.Separator(main_frame, orient="horizontal")
        separator.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(main_frame, text="Kết quả:", font=("Segoe UI", 11, "bold")).grid(
            row=6, column=0, columnspan=3, sticky=tk.W, pady=(10, 5)
        )
        
        result_frame = ttk.Frame(main_frame)
        result_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.result_text = tk.Text(
            result_frame, 
            height=10, 
            width=70, 
            state="disabled",
            font=("Consolas", 9),
            wrap=tk.WORD
        )
        self.result_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        self.open_folder_btn = ttk.Button(
            main_frame,
            text="Mở thư mục kết quả",
            command=self.open_output_folder,
            state="disabled"
        )
        self.open_folder_btn.grid(row=8, column=0, columnspan=3, pady=10)
        
        self.progress_label = ttk.Label(
            main_frame,
            text="",
            font=("Segoe UI", 9),
            foreground="#0066cc"
        )
        self.progress_label.grid(row=9, column=0, columnspan=3, pady=(5, 0))
        
        self.progress = ttk.Progressbar(
            main_frame,
            mode="determinate",
            length=600
        )
        self.progress.grid(row=10, column=0, columnspan=3, pady=5)
        
    def browse_input_file(self):
        file_path = filedialog.askopenfilename(
            title="Chọn file đầu vào",
            filetypes=[
                ("Text files", "*.txt"),
                ("Excel files", "*.xlsx"),
                ("All files", "*.*")
            ]
        )
        if file_path:
            self.input_file_path.set(file_path)
            
    def update_result(self, message, clear=False):
        self.result_text.configure(state="normal")
        if clear:
            self.result_text.delete("1.0", tk.END)
        self.result_text.insert(tk.END, message + "\n")
        self.result_text.see(tk.END)
        self.result_text.configure(state="disabled")
    
    def update_progress(self, current, total, status=""):
        if total > 0:
            percentage = (current / total) * 100
            self.progress['value'] = percentage
            
            if status:
                label_text = f"{status} - {current}/{total} ({percentage:.1f}%)"
            else:
                label_text = f"{current}/{total} ({percentage:.1f}%)"
            
            self.progress_label.config(text=label_text)
        else:
            self.progress['value'] = 0
            self.progress_label.config(text=status)
        
    def start_conversion(self):
        if self.is_converting:
            messagebox.showwarning("Cảnh báo", "Đang xử lý, vui lòng đợi!")
            return
            
        api_key = self.api_key.get().strip()
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
            self.update_result("Đang đọc file đầu vào...", clear=True)
            self.root.after(0, lambda: self.update_progress(10, 100, "Đọc file đầu vào..."))
            
            if file_ext == '.txt':
                addresses = self.read_txt_file(input_file)
            else:
                addresses = self.read_excel_file(input_file)
            
            if not addresses:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "File đầu vào không có dữ liệu!"))
                return
                
            total_addresses = len(addresses)
            self.update_result(f"Đã đọc {total_addresses} địa chỉ từ file")
            self.root.after(0, lambda: self.update_progress(20, 100, "Chuẩn bị xử lý..."))
            
            num_batches = (total_addresses + MAX_BATCH_SIZE - 1) // MAX_BATCH_SIZE
            
            if num_batches > 1:
                self.update_result(f"\n[CẢNH BÁO] File có {total_addresses} địa chỉ, vượt quá giới hạn {MAX_BATCH_SIZE} địa chỉ/lần")
                self.update_result(f"Hệ thống sẽ tự động chia thành {num_batches} lần gửi")
                self.update_result(f"Thời gian chờ giữa các lần: {BATCH_DELAY_SECONDS} giây\n")
            
            api_endpoint = API_ENDPOINT_TEST if api_key == TEST_API_KEY else API_ENDPOINT_PROD
            
            all_results = []
            total_successful = 0
            total_failed = 0
            
            for batch_num in range(num_batches):
                start_idx = batch_num * MAX_BATCH_SIZE
                end_idx = min((batch_num + 1) * MAX_BATCH_SIZE, total_addresses)
                batch_addresses = addresses[start_idx:end_idx]
                
                batch_info = f"Lần {batch_num + 1}/{num_batches}" if num_batches > 1 else ""
                if batch_info:
                    self.update_result(f"{batch_info}: Xử lý địa chỉ {start_idx + 1} đến {end_idx}")
                
                progress_start = 20 + (batch_num * 70 // num_batches)
                self.root.after(0, lambda p=progress_start, b=batch_info: self.update_progress(
                    p, 100, f"Đang gửi yêu cầu {b}..." if b else "Đang gửi yêu cầu..."
                ))
                
                response = requests.post(
                    api_endpoint,
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
                    self.update_result(f"\n[LỖI] {error_msg}")
                    
                    if result_data.get("rateLimited", False):
                        retry_after = result_data.get("retryAfter", 0)
                        self.update_result(f"Vui lòng thử lại sau {retry_after} giây")
                    
                    self.root.after(0, lambda e=error_msg: messagebox.showerror("Lỗi API", e))
                    return
                
                data = result_data.get("data", {})
                batch_successful = data.get("successful", 0)
                batch_failed = data.get("failed", 0)
                batch_results = data.get("results", [])
                
                total_successful += batch_successful
                total_failed += batch_failed
                all_results.extend(batch_results)
                
                if batch_info:
                    self.update_result(f"  → Thành công: {batch_successful}, Thất bại: {batch_failed}")
                
                if batch_num < num_batches - 1:
                    self.update_result(f"Chờ {BATCH_DELAY_SECONDS} giây trước khi gửi lần tiếp theo...")
                    for i in range(BATCH_DELAY_SECONDS):
                        time.sleep(1)
                        remaining = BATCH_DELAY_SECONDS - i - 1
                        if remaining > 0:
                            self.root.after(0, lambda r=remaining: self.progress_label.config(
                                text=f"Chờ {r} giây..."
                            ))
            
            self.root.after(0, lambda: self.update_progress(90, 100, "Đang lưu kết quả..."))
            
            self.update_result(f"\n{'='*50}")
            self.update_result(f"TỔNG KẾT:")
            self.update_result(f"  - Tổng số địa chỉ: {total_addresses}")
            self.update_result(f"  - Thành công: {total_successful}")
            self.update_result(f"  - Thất bại: {total_failed}")
            if num_batches > 1:
                self.update_result(f"  - Số lần gửi: {num_batches}")
            self.update_result(f"{'='*50}\n")
            
            input_path = Path(input_file)
            output_folder = input_path.parent / "output"
            output_folder.mkdir(exist_ok=True)
            self.output_folder = str(output_folder)
            
            output_filename = f"{input_path.stem}_converted{file_ext}"
            output_path = output_folder / output_filename
            
            if file_ext == '.txt':
                self.write_txt_output(output_path, all_results)
            else:
                self.write_excel_output(output_path, all_results)
            
            self.update_result(f"Đã lưu kết quả tại:\n{output_path}")
            self.root.after(0, lambda: self.update_progress(100, 100, "Hoàn thành!"))
            
            self.root.after(0, lambda: self.open_folder_btn.configure(state="normal"))
            self.root.after(0, lambda s=total_successful, f=total_failed, fn=output_filename: messagebox.showinfo(
                "Hoàn thành", 
                f"Chuyển đổi thành công!\n\nThành công: {s}\nThất bại: {f}\n\nFile kết quả: {fn}"
            ))
            
        except requests.exceptions.Timeout:
            self.update_result("\n[LỖI] Timeout - Không thể kết nối đến API")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến API (Timeout)"))
        except requests.exceptions.ConnectionError:
            self.update_result("\n[LỖI] Không thể kết nối đến server")
            if api_key == TEST_API_KEY:
                self.update_result("Hãy chắc chắn test server đang chạy tại http://localhost:5000")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể kết nối đến server"))
        except Exception as e:
            self.update_result(f"\n[LỖI] {str(e)}")
            self.root.after(0, lambda e=str(e): messagebox.showerror("Lỗi", f"Lỗi xử lý: {e}"))
        finally:
            self.is_converting = False
            self.root.after(0, lambda: self.convert_btn.configure(state="normal"))
            self.root.after(0, lambda: self.progress_label.config(text=""))
            
    def read_txt_file(self, file_path):
        addresses = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        addresses.append(line)
        except Exception as e:
            self.update_result(f"[LỖI] Không thể đọc file txt: {str(e)}")
        return addresses
        
    def read_excel_file(self, file_path):
        addresses = []
        try:
            wb = openpyxl.load_workbook(file_path, read_only=True)
            ws = wb.active
            
            for row in ws.iter_rows(min_row=1, values_only=True):
                if row and row[0]:
                    addr = str(row[0]).strip()
                    if addr:
                        addresses.append(addr)
            wb.close()
        except Exception as e:
            self.update_result(f"[LỖI] Không thể đọc file Excel: {str(e)}")
        return addresses
        
    def write_txt_output(self, output_path, results):
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for result in results:
                    if result.get("success", False):
                        f.write(result.get("converted", "") + "\n")
                    else:
                        error_msg = result.get("error", "Lỗi không xác định")
                        f.write(f"LỖI: {error_msg}\n")
        except Exception as e:
            self.update_result(f"[LỖI] Không thể ghi file txt: {str(e)}")
            
    def write_excel_output(self, output_path, results):
        try:
            wb = Workbook()
            ws = wb.active
            ws.title = "Kết quả"
            
            header_font = Font(bold=True, size=11)
            header_fill = PatternFill(start_color="366092", end_color="366092", fill_type="solid")
            header_alignment = Alignment(horizontal="center", vertical="center")
            
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
            self.update_result(f"[LỖI] Không thể ghi file Excel: {str(e)}")
            
    def open_output_folder(self):
        if self.output_folder and os.path.exists(self.output_folder):
            os.startfile(self.output_folder)
        else:
            messagebox.showerror("Lỗi", "Thư mục kết quả không tồn tại!")


def main():
    root = tk.Tk()
    
    style = ttk.Style()
    style.theme_use('vista')
    style.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))
    
    app = AddressConverterApp(root)
    
    root.mainloop()


if __name__ == "__main__":
    main()
