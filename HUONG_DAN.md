# HƯỚNG DẪN SỬ DỤNG - Ứng dụng Chuyển đổi địa chỉ 2 cấp

## Giới thiệu giao diện

Ứng dụng sử dụng **CustomTkinter** - framework UI hiện đại với:
- Light theme sáng sủa, dễ nhìn
- Rounded corners và smooth animations
- Professional color scheme (Blue theme)
- Responsive layout với window size 800x650

## Cài đặt môi trường phát triển

### Bước 1: Tạo môi trường conda
```powershell
cd d:\Github\Code-Python\DiaChi2Cap
conda create -n dia-chi-2-cap python=3.11 -y
conda activate dia-chi-2-cap
```

### Bước 2: Cài đặt dependencies
```powershell
pip install -r requirements.txt
```

Các thư viện chính:
- **customtkinter 5.2.2**: Modern UI components
- **darkdetect**: Auto theme detection
- **requests**: API communication
- **openpyxl**: Excel processing
- **flask**: Development test server
- **pyinstaller**: Portable exe builder

## Chạy ứng dụng trong môi trường development

### Chạy test server (Terminal 1)
```powershell
conda activate dia-chi-2-cap
.\run_test.ps1
```

Test server sẽ chạy tại: `http://localhost:5000`

API Key test: `testing-chuyen-doi-2-cap`

### Chạy ứng dụng GUI (Terminal 2)
```powershell
conda activate dia-chi-2-cap
python app.py
```

## Build file exe portable

### Cách 1: Build tự động với script (khuyến nghị)
```powershell
.\build_exe.ps1
```

### Cách 2: Build với file spec có sẵn
```powershell
conda activate dia-chi-2-cap
pyinstaller app.spec --clean --noconfirm
```

File exe sẽ được tạo tại: `dist\ChuyenDoiDiaChi.exe`

## Cấu trúc thư mục sau khi build

```
DiaChi2Cap/
├── app.py                    # File chính ứng dụng GUI
├── test_server.py            # Server test local
├── requirements.txt          # Dependencies
├── app.spec                 # PyInstaller config
├── guide.md                 # API documentation
├── HUONG_DAN.md            # File này
├── build/                   # Thư mục build tạm (có thể xóa)
├── dist/                    # Thư mục chứa exe
│   └── ChuyenDoiDiaChi.exe
└── output/                  # Thư mục kết quả (tự động tạo)
```

## Sử dụng ứng dụng

### Test mode (với localhost server)
1. Mở Terminal 1, chạy test server
2. Mở ứng dụng
3. Nhập API Key: `testing-chuyen-doi-2-cap`
4. Chọn file đầu vào (.txt hoặc .xlsx)
5. Click "CHUYỂN ĐỔI"
6. Theo dõi progress bar và kết quả
7. Kết quả sẽ lưu trong thư mục `output`

### Production mode (với API thật)
1. Mở ứng dụng
2. Nhập API Key thật của bạn
3. Chọn file đầu vào (.txt hoặc .xlsx)
4. Click "CHUYỂN ĐỔI"
5. Theo dõi progress bar và kết quả
6. Kết quả sẽ lưu trong thư mục `output`

## Xử lý file lớn (> 1000 địa chỉ)

### Tính năng Auto-Batch
Khi file đầu vào có nhiều hơn 1000 địa chỉ, ứng dụng sẽ:

1. **Cảnh báo**: Hiển thị thông báo về số lượng địa chỉ và số batch cần xử lý
   ```
   [CẢNH BÁO] File có 2500 địa chỉ, vượt quá giới hạn 1000 địa chỉ/lần
   Hệ thống sẽ tự động chia thành 3 lần gửi
   Thời gian chờ giữa các lần: 5 giây
   ```

2. **Tự động chia nhỏ**: Chia file thành các batch, mỗi batch tối đa 1000 địa chỉ

3. **Progress bar**: Hiển thị tiến trình xử lý chi tiết
   - Đọc file: 0-20%
   - Xử lý các batch: 20-90%
   - Lưu kết quả: 90-100%

4. **Delay giữa các batch**: Chờ 5 giây giữa mỗi lần gửi để tránh rate limit

5. **Tổng hợp kết quả**: Kết hợp kết quả từ tất cả các batch vào một file

### Ví dụ xử lý 2500 địa chỉ
```
Đã đọc 2500 địa chỉ từ file

[CẢNH BÁO] File có 2500 địa chỉ, vượt quá giới hạn 1000 địa chỉ/lần
Hệ thống sẽ tự động chia thành 3 lần gửi
Thời gian chờ giữa các lần: 5 giây

Lần 1/3: Xử lý địa chỉ 1 đến 1000
  → Thành công: 950, Thất bại: 50
Chờ 5 giây trước khi gửi lần tiếp theo...

Lần 2/3: Xử lý địa chỉ 1001 đến 2000
  → Thành công: 960, Thất bại: 40
Chờ 5 giây trước khi gửi lần tiếp theo...

Lần 3/3: Xử lý địa chỉ 2001 đến 2500
  → Thành công: 480, Thất bại: 20

==================================================
TỔNG KẾT:
  - Tổng số địa chỉ: 2500
  - Thành công: 2390
  - Thất bại: 110
  - Số lần gửi: 3
==================================================
```

## Format file đầu vào

### File TXT
- Mỗi dòng là 1 địa chỉ
- Encoding: UTF-8
- Ví dụ:
```
470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng
54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng
```

### File Excel (.xlsx)
- Cột đầu tiên (cột A) chứa địa chỉ
- Có thể có hoặc không có header
- Ví dụ:

| A (Địa chỉ) |
|-------------|
| 470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng |
| 54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng |

## Format file kết quả

### File TXT output
```
470 Đ. Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng
LỖI: Không tìm thấy địa chỉ tương ứng trong dữ liệu.
54 Nguyễn Lương Bằng, Phường Hòa Khánh Bắc, Quận Liên Chiểu, Thành phố Đà Nẵng
```

### File Excel output
| Gốc | Chuyển đổi |
|-----|------------|
| 470 Đ. Trần Đại Nghĩa, Hoà Hải... | 470 Đ. Trần Đại Nghĩa, Phường Hòa Hải... |
| Địa chỉ sai | LỖI: Không tìm thấy địa chỉ... |

## Giới hạn và xử lý

### Giới hạn API
- Tối đa 1000 địa chỉ/request (API endpoint)
- Rate limit: 1 request/5 phút (theo API)
- Timeout: 60 giây/request

### Xử lý của ứng dụng
- ✅ **File lớn**: Tự động chia nhỏ thành nhiều batch
- ✅ **Delay tự động**: Chờ 5 giây giữa các batch
- ✅ **Progress bar**: Hiển thị tiến trình xử lý
- ✅ **Tổng hợp kết quả**: Kết hợp tất cả batch vào 1 file output

### Test với file lớn
Tạo file test lớn để kiểm tra tính năng auto-batch:
```powershell
python create_test_large.py
```
Sẽ tạo:
- `test_input_large.txt`: 1500 địa chỉ (2 batch)
- `test_input_large.xlsx`: 2500 địa chỉ (3 batch)

## Xử lý lỗi

### Lỗi "Không thể kết nối đến server"
- Với test mode: Đảm bảo test server đang chạy
- Với production: Kiểm tra kết nối internet

### Lỗi "API key không hợp lệ"
- Kiểm tra lại API key
- Đảm bảo không có khoảng trắng thừa

### Lỗi "Rate limited"
- Đợi thời gian quy định (hiển thị trong thông báo)
- Thử lại sau

## Lưu ý portable

File exe đã được build với PyInstaller:
- Không cần cài Python
- Chạy được trên Windows 10/11
- Kích thước khoảng 15-20MB
- Có thể copy sang máy khác và chạy trực tiếp
- Không cần cài đặt thêm thư viện

## Troubleshooting

### File exe không chạy được
1. Kiểm tra Windows Defender/Antivirus
2. Chạy với quyền Administrator
3. Kiểm tra Windows version (cần Windows 10+)

### Lỗi khi build exe
```powershell
# Xóa cache và build lại
Remove-Item -Recurse -Force build, dist
pyinstaller app.spec --clean --noconfirm
```

### Test địa chỉ mẫu (cho test server)
Các địa chỉ này sẽ convert thành công với test server:
- 470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng
- 54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng
- 470 Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng

Các địa chỉ khác sẽ trả về lỗi "Không tìm thấy địa chỉ..."

## Liên hệ hỗ trợ

Nếu gặp vấn đề, vui lòng kiểm tra:
1. Log trong ứng dụng (ô "Kết quả")
2. API documentation tại `guide.md`
3. Test với localhost server trước
