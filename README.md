# Ứng dụng Chuyển đổi địa chỉ 2 cấp

Ứng dụng Windows portable với giao diện hiện đại để chuyển đổi địa chỉ từ định dạng cũ sang định dạng mới (2 cấp) sử dụng API từ address-converter.io.vn

## Tính năng

- ✅ **Giao diện hiện đại với CustomTkinter**: Light theme, rounded corners, professional UI
- ✅ Giao diện tiếng Việt đơn giản, dễ sử dụng
- ✅ Hỗ trợ file đầu vào: TXT và Excel (.xlsx)
- ✅ **Xử lý tự động với file lớn**: Tự động chia nhỏ và gửi nhiều batch khi vượt quá 1000 địa chỉ
- ✅ **Progress bar chi tiết**: Hiển thị tiến trình xử lý theo thời gian thực
- ✅ Hiển thị kết quả chi tiết (thành công/thất bại)
- ✅ Tự động tạo file kết quả trong thư mục output
- ✅ Xử lý lỗi rate limiting với retry logic
- ✅ Test mode với localhost server

## Cài đặt nhanh

### Yêu cầu
- Windows 10/11
- Anaconda/Miniconda đã cài đặt

### Bước 1: Tạo môi trường
```powershell
cd d:\Github\Code-Python\DiaChi2Cap
conda create -n dia-chi-2-cap python=3.11 -y
conda activate dia-chi-2-cap
```

### Bước 2: Cài đặt dependencies
```powershell
pip install -r requirements.txt
```

Requirements bao gồm:
- **customtkinter**: Modern UI framework với dark theme
- **requests**: HTTP client cho API calls
- **openpyxl**: Excel file handling
- **flask**: Test server
- **pyinstaller**: Build portable exe

### Bước 3: Tạo file test
```powershell
python create_test_excel.py

# (Tùy chọn) Tạo file test lớn để kiểm tra auto-batch
python create_test_large.py
```

## Tính năng mới: Xử lý tự động file lớn

### Auto-Batch Processing
Khi file đầu vào có **hơn 1000 địa chỉ**, ứng dụng sẽ:
1. ⚠️ Hiển thị cảnh báo về số lượng địa chỉ vượt quá giới hạn
2. 🔄 Tự động chia nhỏ thành nhiều batch (mỗi batch ≤ 1000 địa chỉ)
3. ⏱️ Gửi từng batch với delay 5 giây giữa các lần gửi
4. 📊 Hiển thị progress bar chi tiết cho từng batch
5. ✅ Tổng hợp kết quả từ tất cả các batch

**Ví dụ**: File có 2500 địa chỉ sẽ được xử lý như sau:
- Batch 1: Địa chỉ 1-1000 → Gửi API
- Chờ 5 giây
- Batch 2: Địa chỉ 1001-2000 → Gửi API
- Chờ 5 giây
- Batch 3: Địa chỉ 2001-2500 → Gửi API
- Tổng hợp và lưu kết quả

### Progress Bar
Progress bar hiển thị:
- Phần trăm hoàn thành (0-100%)
- Trạng thái hiện tại ("Đang đọc file...", "Đang gửi yêu cầu...", v.v.)
- Số lượng batch đang xử lý (nếu có nhiều batch)
- Thời gian chờ giữa các batch

## Sử dụng

### Development mode

#### Chạy test server (Terminal 1)
```powershell
conda activate dia-chi-2-cap
.\run_test.ps1
```

#### Chạy ứng dụng (Terminal 2)
```powershell
conda activate dia-chi-2-cap
python app.py
```

### Production mode - Build exe portable

#### Cách 1: Tự động (khuyến nghị)
```powershell
.\build_exe.ps1
```

#### Cách 2: Thủ công
```powershell
conda activate dia-chi-2-cap
pyinstaller app.spec --clean --noconfirm
```

File exe sẽ được tạo tại: `dist\ChuyenDoiDiaChi.exe`

## Cấu trúc project

```
DiaChi2Cap/
├── app.py                      # Ứng dụng chính (GUI)
├── test_server.py              # Test server mock API
├── create_test_excel.py        # Script tạo file test Excel
├── create_test_large.py        # Script tạo file test lớn (>1000 địa chỉ)
├── test_syntax.py              # Script kiểm tra cú pháp
├── requirements.txt            # Python dependencies
├── app.spec                   # PyInstaller config
├── build_exe.ps1              # Script build exe tự động (PowerShell)
├── run_test.ps1               # Script test nhanh (PowerShell)
├── test_input.txt             # File test TXT
├── test_input.xlsx            # File test Excel (tạo tự động)
├── guide.md                   # API documentation
├── HUONG_DAN.md              # Hướng dẫn chi tiết
└── README.md                  # File này
```

## Hướng dẫn test

### Test với localhost server

1. Mở Terminal 1:
```powershell
conda activate dia-chi-2-cap
python test_server.py
```

2. Mở Terminal 2:
```powershell
conda activate dia-chi-2-cap
python app.py
```

3. Trong ứng dụng:
   - API Key: `testing-chuyen-doi-2-cap`
   - Chọn file: `test_input.txt` hoặc `test_input.xlsx`
   - Click "CHUYỂN ĐỔI"

4. Kiểm tra kết quả trong thư mục `output`

### Test với API thật

1. Mở ứng dụng
2. Nhập API Key thật (từ address-converter.io.vn)
3. Chọn file đầu vào
4. Click "CHUYỂN ĐỔI"

## Format file đầu vào

### File TXT
Mỗi dòng là một địa chỉ:
```
470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng
54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng
```

### File Excel
Cột A chứa địa chỉ (có thể có header):

| Địa chỉ |
|---------|
| 470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng |
| 54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng |

## Format file kết quả

### TXT output
```
470 Đ. Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng
LỖI: Không tìm thấy địa chỉ tương ứng trong dữ liệu.
```

### Excel output

| Gốc | Chuyển đổi |
|-----|------------|
| 470 Đ. Trần Đại Nghĩa... | 470 Đ. Trần Đại Nghĩa, Phường Hòa Hải... |
| Địa chỉ sai | LỖI: Không tìm thấy địa chỉ... |

## Giới hạn

- Tối đa: 1000 địa chỉ/request
- Rate limit: 1 request/5 phút
- Timeout: 60 giây
- Encoding: UTF-8

## Kiểm tra cú pháp

```powershell
python test_syntax.py
```

## Troubleshooting

### Lỗi import khi phát triển
```powershell
pip install -r requirements.txt
```

### Build exe thất bại
```powershell
# Xóa cache
rmdir /s /q build dist
# Build lại
pyinstaller app.spec
```

### Exe không chạy
- Kiểm tra Windows Defender
- Chạy với quyền Administrator
- Kiểm tra Windows version (yêu cầu Windows 10+)

### Test server không chạy
```powershell
# Kiểm tra port 5000 có bị chiếm không
netstat -ano | findstr :5000
# Nếu có, kill process hoặc đổi port trong test_server.py
```

## Test mode addresses

Các địa chỉ này sẽ convert thành công với test server:
- `470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng`
- `54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng`
- `470 Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng`

Các địa chỉ khác sẽ trả về lỗi.

## API Reference

Xem chi tiết tại [guide.md](guide.md)

## License

MIT

## Tác giả

Developed for địa chỉ 2 cấp conversion project
