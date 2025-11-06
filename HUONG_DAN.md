# HƯỚNG DẪN KỸ THUẬT - Ứng dụng Chuyển đổi địa chỉ 2 cấp# HƯỚNG DẪN SỬ DỤNG - Ứng dụng Chuyển đổi địa chỉ 2 cấp



## Dành cho Developers## Giới thiệu giao diện



---Ứng dụng sử dụng **CustomTkinter** - framework UI hiện đại với:

- Light theme sáng sủa, dễ nhìn

## 1. TỔNG QUAN KIẾN TRÚC- Rounded corners và smooth animations

- Professional color scheme (Blue theme)

### 1.1 Tech Stack- Responsive layout với window size 800x650

- **Python**: 3.11+

- **GUI Framework**: CustomTkinter 5.2.2## Cài đặt môi trường phát triển

- **HTTP Client**: requests

- **Excel Processing**: openpyxl### Bước 1: Tạo môi trường conda

- **Geocoding APIs**: Goong.io, OpenMap.vn```powershell

cd d:\Github\Code-Python\DiaChi2Cap

### 1.2 Cấu trúc thư mụcconda create -n dia-chi-2-cap python=3.11 -y

conda activate dia-chi-2-cap

``````

DiaChi2Cap/

├── app.py                          # GUI application (main entry point)### Bước 2: Cài đặt dependencies

├── modules/```powershell

│   ├── __init__.pypip install -r requirements.txt

│   ├── api_client.py               # API communication layer```

│   ├── conversion_processor.py    # Business logic & multi-stage processing

│   ├── file_handlers.py            # File I/O operationsCác thư viện chính:

│   └── utils.py                    # Constants & utilities- **customtkinter 5.2.2**: Modern UI components

├── output/                         # Generated output files- **darkdetect**: Auto theme detection

├── requirements.txt                # Python dependencies- **requests**: API communication

├── test_syntax.py                  # Syntax validation- **openpyxl**: Excel processing

├── test_validation.py              # Integration tests- **flask**: Development test server

└── HUONG_DAN.md                   # This file- **pyinstaller**: Portable exe builder

```

## Chạy ứng dụng trong môi trường development

### 1.3 Kiến trúc 3-Layer

### Chạy test server (Terminal 1)

``````powershell

┌─────────────────────────────────────┐conda activate dia-chi-2-cap

│  GUI Layer (app.py)                 │.\run_test.ps1

│  - CustomTkinter UI                 │```

│  - User interaction                 │

│  - Progress tracking                │Test server sẽ chạy tại: `http://localhost:5000`

└────────────┬────────────────────────┘

             │API Key test: `testing-chuyen-doi-2-cap`

┌────────────▼────────────────────────┐

│  Business Logic Layer                │### Chạy ứng dụng GUI (Terminal 2)

│  (conversion_processor.py)           │```powershell

│  - Multi-stage processing            │conda activate dia-chi-2-cap

│  - Batch handling                    │python app.py

│  - Geocoding fallback                │```

│  - Multi-threading coordination      │

└────────────┬────────────────────────┘## Build file exe portable

             │

┌────────────▼────────────────────────┐### Cách 1: Build tự động với script (khuyến nghị)

│  Data Access Layer                   │```powershell

│  - api_client.py: HTTP calls         │.\build_exe.ps1

│  - file_handlers.py: File I/O        │```

│  - utils.py: Helpers & constants     │

└─────────────────────────────────────┘### Cách 2: Build với file spec có sẵn

``````powershell

conda activate dia-chi-2-cap

---pyinstaller app.spec --clean --noconfirm

```

## 2. THIẾT LẬP MÔI TRƯỜNG

File exe sẽ được tạo tại: `dist\ChuyenDoiDiaChi.exe`

### 2.1 Cài đặt với Conda (Khuyến nghị)

## Cấu trúc thư mục sau khi build

```powershell

# Tạo môi trường mới```

conda create -n dia-chi-2-cap python=3.11 -yDiaChi2Cap/

├── app.py                    # File chính ứng dụng GUI

# Kích hoạt môi trường├── test_server.py            # Server test local

conda activate dia-chi-2-cap├── requirements.txt          # Dependencies

├── app.spec                 # PyInstaller config

# Cài đặt dependencies├── guide.md                 # API documentation

pip install -r requirements.txt├── HUONG_DAN.md            # File này

```├── build/                   # Thư mục build tạm (có thể xóa)

├── dist/                    # Thư mục chứa exe

### 2.2 Cài đặt với pip (Alternative)│   └── ChuyenDoiDiaChi.exe

└── output/                  # Thư mục kết quả (tự động tạo)

```powershell```

# Tạo virtual environment

python -m venv venv## Sử dụng ứng dụng



# Kích hoạt (Windows)### Test mode (với localhost server)

.\venv\Scripts\activate1. Mở Terminal 1, chạy test server

2. Mở ứng dụng

# Cài đặt dependencies3. Nhập API Key: `testing-chuyen-doi-2-cap`

pip install -r requirements.txt4. Chọn file đầu vào (.txt hoặc .xlsx)

```5. Click "CHUYỂN ĐỔI"

6. Theo dõi progress bar và kết quả

### 2.3 Dependencies (requirements.txt)7. Kết quả sẽ lưu trong thư mục `output`



```txt### Production mode (với API thật)

customtkinter==5.2.21. Mở ứng dụng

darkdetect2. Nhập API Key thật của bạn

requests3. Chọn file đầu vào (.txt hoặc .xlsx)

openpyxl4. Click "CHUYỂN ĐỔI"

flask  # Chỉ cần cho test server5. Theo dõi progress bar và kết quả

```6. Kết quả sẽ lưu trong thư mục `output`



---## Xử lý file lớn (> 1000 địa chỉ)



## 3. CẤU HÌNH API### Tính năng Auto-Batch

Khi file đầu vào có nhiều hơn 1000 địa chỉ, ứng dụng sẽ:

### 3.1 File cấu hình: `modules/utils.py`

1. **Cảnh báo**: Hiển thị thông báo về số lượng địa chỉ và số batch cần xử lý

```python   ```

# API Keys   [CẢNH BÁO] File có 2500 địa chỉ, vượt quá giới hạn 1000 địa chỉ/lần

TEST_API_KEY = "testing-chuyen-doi-2-cap"   Hệ thống sẽ tự động chia thành 3 lần gửi

API_DOMAIN_PROD = "https://address-converter.io.vn"   Thời gian chờ giữa các lần: 5 giây

API_DOMAIN_TEST = "http://localhost:5000"   ```



# Geocoding API Keys2. **Tự động chia nhỏ**: Chia file thành các batch, mỗi batch tối đa 1000 địa chỉ

GOONG_API_KEY = "your-goong-api-key"      # Hoặc "blank" để tắt

OPENMAP_API_KEY = "your-openmap-api-key"  # Hoặc "blank" để tắt3. **Progress bar**: Hiển thị tiến trình xử lý chi tiết

   - Đọc file: 0-20%

# Batch processing limits   - Xử lý các batch: 20-90%

MAX_ADDRESS_BATCH_SIZE = 1000  # Địa chỉ/request   - Lưu kết quả: 90-100%

BATCH_DELAY_SECONDS = 2        # Delay giữa các batch

OPENMAP_RATE_LIMIT_DELAY = 0.2 # Rate limit cho OpenMap (0.2s)4. **Delay giữa các batch**: Chờ 5 giây giữa mỗi lần gửi để tránh rate limit

```

5. **Tổng hợp kết quả**: Kết hợp kết quả từ tất cả các batch vào một file

### 3.2 API Endpoints

### Tính năng Auto-Retry khi Rate Limit

#### 3.2.1 Address Conversion APIKhi gặp lỗi rate limit từ API, ứng dụng sẽ:

- **Production**: `https://address-converter.io.vn`

- **Local Test**: `http://localhost:5000`1. **Phát hiện rate limit**: Nhận diện response có `rateLimited: true`



**Endpoint: POST /api/convert-batch**2. **Hiển thị thông báo**: 

```json   ```

{   [RATE LIMIT] Chức năng chuyển đổi hàng loạt chỉ cho phép 1 lần sử dụng trong 5 phút...

  "addresses": ["địa chỉ 1", "địa chỉ 2", ...],   Tự động thử lại sau 21 giây...

  "key": "your-api-key"   ```

}

```3. **Countdown real-time**: Progress bar hiển thị thời gian chờ còn lại

   ```

**Response:**   Rate limited - Chờ 20 giây...

```json   Rate limited - Chờ 19 giây...

{   Rate limited - Chờ 18 giây...

  "success": true,   ```

  "data": {

    "results": [4. **Tự động retry**: Sau khi hết thời gian chờ, gửi lại request tự động

      {   ```

        "original": "Phường Bến Nghé, Quận 1, TP HCM",   Đang thử lại lần 1/3...

        "converted": "Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh",   ```

        "success": true

      }5. **Xử lý kết quả retry**:

    ]   - Nếu thành công: Tiếp tục xử lý bình thường

  }   - Nếu thất bại: Hiển thị lỗi và dừng

}

```**Lưu ý**: Tính năng này hoàn toàn tự động, không cần can thiệp thủ công!

   ```

**Endpoint: POST /api/convert-coordinate**

```json2. **Tự động chia nhỏ**: Chia file thành các batch, mỗi batch tối đa 1000 địa chỉ

{

  "coordinates": [3. **Progress bar**: Hiển thị tiến trình xử lý chi tiết

    {"longitude": 106.7, "latitude": 10.8}   - Đọc file: 0-20%

  ],   - Xử lý các batch: 20-90%

  "key": "your-api-key"   - Lưu kết quả: 90-100%

}

```4. **Delay giữa các batch**: Chờ 5 giây giữa mỗi lần gửi để tránh rate limit



#### 3.2.2 Goong Geocoding API5. **Tổng hợp kết quả**: Kết hợp kết quả từ tất cả các batch vào một file



**Endpoint: GET /geocode**### Ví dụ xử lý 2500 địa chỉ

``````

https://rsapi.goong.io/geocode?address={encoded_address}&api_key={key}Đã đọc 2500 địa chỉ từ file

```

[CẢNH BÁO] File có 2500 địa chỉ, vượt quá giới hạn 1000 địa chỉ/lần

**Response structure:**Hệ thống sẽ tự động chia thành 3 lần gửi

```jsonThời gian chờ giữa các lần: 5 giây

{

  "status": "OK",Lần 1/3: Xử lý địa chỉ 1 đến 1000

  "results": [  → Thành công: 950, Thất bại: 50

    {Chờ 5 giây trước khi gửi lần tiếp theo...

      "geometry": {

        "location": {Lần 2/3: Xử lý địa chỉ 1001 đến 2000

          "lat": 21.0137443,  → Thành công: 960, Thất bại: 40

          "lng": 105.7983461Chờ 5 giây trước khi gửi lần tiếp theo...

        }

      },Lần 3/3: Xử lý địa chỉ 2001 đến 2500

      "formatted_address": "91 Trung Kính, Trung Hòa, Cầu Giấy, Hà Nội"  → Thành công: 480, Thất bại: 20

    }

  ]==================================================

}TỔNG KẾT:

```  - Tổng số địa chỉ: 2500

  - Thành công: 2390

**Lưu ý**: Goong trả về `lat, lng` (vĩ độ trước)  - Thất bại: 110

  - Số lần gửi: 3

#### 3.2.3 OpenMap Geocoding API==================================================

```

**Endpoint: GET /v1/geocode/forward**

```## Format file đầu vào

https://mapapis.openmap.vn/v1/geocode/forward?address={encoded_address}&apikey={key}

```### File TXT

- Mỗi dòng là 1 địa chỉ

**Response structure:**- Encoding: UTF-8

```json- Ví dụ:

{```

  "status": "OK",470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng

  "results": [54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng

    {```

      "geometry": {

        "location": {### File Excel (.xlsx)

          "lat": 21.032783,- Cột đầu tiên (cột A) chứa địa chỉ

          "lng": 105.787915- Có thể có hoặc không có header

        }- Ví dụ:

      }

    }| A (Địa chỉ) |

  ]|-------------|

}| 470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng |

```| 54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng |



**Lưu ý**: OpenMap cũng trả về `lat, lng` trong format Google-compatible## Format file kết quả



---### File TXT output

```

## 4. LUỒNG XỬ LÝ CHÍNH (MULTI-STAGE PROCESSING)470 Đ. Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng

LỖI: Không tìm thấy địa chỉ tương ứng trong dữ liệu.

### 4.1 Tổng quan 6 bước54 Nguyễn Lương Bằng, Phường Hòa Khánh Bắc, Quận Liên Chiểu, Thành phố Đà Nẵng

```

```

[BƯỚC 1] CHUẨN BỊ DỮ LIỆU### File Excel output

    ├─ Pre-conversion (ánh xạ đặc biệt)| Gốc | Chuyển đổi |

    ├─ Tạo 2 phiên bản: có tên đường & không tên đường|-----|------------|

    └─ Multi-threading cho chuẩn hóa| 470 Đ. Trần Đại Nghĩa, Hoà Hải... | 470 Đ. Trần Đại Nghĩa, Phường Hòa Hải... |

| Địa chỉ sai | LỖI: Không tìm thấy địa chỉ... |

[BƯỚC 2] XỬ LÝ ĐỊA CHỈ CHI TIẾT (với tên đường)

    ├─ Batch đầu: 10 địa chỉ (kiểm tra nhanh)## Giới hạn và xử lý

    ├─ Các batch tiếp: 100 địa chỉ/batch

    └─ Sử dụng API /convert-batch### Giới hạn API

- Tối đa 1000 địa chỉ/request (API endpoint)

[BƯỚC 3] XỬ LÝ 3 CẤP CƠ BẢN (không tên đường)- Rate limit: 1 request/5 phút (theo API)

    ├─ Chỉ xử lý địa chỉ bị lỗi từ Bước 2- Timeout: 60 giây/request

    ├─ Loại bỏ số nhà/đường

    ├─ Batch size: 1000 địa chỉ### Xử lý của ứng dụng

    └─ Smart retry nếu len(results) != len(sent)- ✅ **File lớn**: Tự động chia nhỏ thành nhiều batch

- ✅ **Delay tự động**: Chờ 5 giây giữa các batch

[BƯỚC 4] OPENMAP GEOCODING (có tên đường)- ✅ **Progress bar**: Hiển thị tiến trình xử lý

    ├─ Multi-threading: 5 workers- ✅ **Tổng hợp kết quả**: Kết hợp tất cả batch vào 1 file output

    ├─ Rate limit: 0.2s giữa các request

    ├─ Thu thập coordinates### Test với file lớn

    └─ Batch coordinate conversion (10 coords/batch)Tạo file test lớn để kiểm tra tính năng auto-batch:

```powershell

[BƯỚC 5] OPENMAP GEOCODING (không tên đường)python create_test_large.py

    ├─ Tương tự Bước 4```

    └─ Fallback cho Bước 4Sẽ tạo:

- `test_input_large.txt`: 1500 địa chỉ (2 batch)

[BƯỚC 6] GOONG GEOCODING (có tên đường)- `test_input_large.xlsx`: 2500 địa chỉ (3 batch)

    ├─ Multi-threading: 10 workers (nhanh hơn OpenMap)

    ├─ Không có rate limit## Xử lý lỗi

    └─ Batch coordinate conversion

```### Lỗi "Không thể kết nối đến server"

- Với test mode: Đảm bảo test server đang chạy

### 4.2 Code Flow (Pseudo-code)- Với production: Kiểm tra kết nối internet



```python### Lỗi "API key không hợp lệ"

# app.py: perform_conversion()- Kiểm tra lại API key

def perform_conversion(api_key, input_file, file_ext):- Đảm bảo không có khoảng trắng thừa

    # 1. Đọc file

    data, headers = read_file(input_file)### Lỗi "Rate limited"

    - Đợi thời gian quy định (hiển thị trong thông báo)

    # 2. Khởi tạo processor- Thử lại sau

    processor = ConversionProcessor(...)

    ## Lưu ý portable

    # 3. Chuẩn bị dữ liệu

    addr_with_street, addr_no_street, original_data, pre_converted = \File exe đã được build với PyInstaller:

        processor.prepare_addresses(data, is_multi_column)- Không cần cài Python

    - Chạy được trên Windows 10/11

    # 4. Bước 2: Xử lý chi tiết- Kích thước khoảng 15-20MB

    results, success, failed, failed_set = \- Có thể copy sang máy khác và chạy trực tiếp

        processor.process_single_parallel(addr_with_street, skipped)- Không cần cài đặt thêm thư viện

    

    # 5. Bước 3: Xử lý 3 cấp cơ bản## Troubleshooting

    results, success, failed, failed_set = \

        processor.process_batch_retry(addr_no_street, results, failed_set)### File exe không chạy được

    1. Kiểm tra Windows Defender/Antivirus

    # 6. Bước 4-6: Geocoding fallback2. Chạy với quyền Administrator

    results, geocoded_success = \3. Kiểm tra Windows version (cần Windows 10+)

        processor.geocode_fallback_openmap_goong(

            addr_with_street, addr_no_street, results, failed_set### Lỗi khi build exe

        )```powershell

    # Xóa cache và build lại

    # 7. Lưu kết quảRemove-Item -Recurse -Force build, dist

    write_output(output_path, results)pyinstaller app.spec --clean --noconfirm

``````



---### Test địa chỉ mẫu (cho test server)

Các địa chỉ này sẽ convert thành công với test server:

## 5. PERFORMANCE OPTIMIZATION- 470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng

- 54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng

### 5.1 So sánh hiệu suất- 470 Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng



**Trước (Sequential):**Các địa chỉ khác sẽ trả về lỗi "Không tìm thấy địa chỉ..."

```

100 địa chỉ lỗi:## Liên hệ hỗ trợ

- Geocode: 100 request × 1s = 100s

- Coordinate conversion: 100 request × 0.5s = 50sNếu gặp vấn đề, vui lòng kiểm tra:

Tổng: ~150 giây1. Log trong ứng dụng (ô "Kết quả")

```2. API documentation tại `guide.md`

3. Test với localhost server trước

**Sau (Parallel + Batch):**
```
100 địa chỉ lỗi:
- Geocode: 100 / 5 workers = 20s
- Coordinate conversion: 100 / 10 (batch) × 5s = 50s
Tổng: ~25 giây (NHANH HƠN 6 LẦN)
```

---

## 6. BUILD PORTABLE EXE

### 6.1 Build Commands

```powershell
# Cách 1: Sử dụng script (khuyến nghị)
.\build_exe.ps1

# Cách 2: Manual build
pyinstaller app.spec --clean --noconfirm

# Output: dist\ChuyenDoiDiaChi.exe
```

---

## 7. TESTING

### 7.1 Test Server

```powershell
# Chạy test server
python test_server.py
# API Key: "testing-chuyen-doi-2-cap"
```

### 7.2 Syntax Validation

```powershell
python test_syntax.py
python -m py_compile app.py
```

---

## 8. TROUBLESHOOTING

### 8.1 Common Issues

**Module not found:**
```powershell
pip install -r requirements.txt
```

**Rate Limit:**
```python
# Tăng delays trong utils.py
BATCH_DELAY_SECONDS = 5
OPENMAP_RATE_LIMIT_DELAY = 0.5
```

**Memory Error:**
```python
# Giảm batch size
MAX_ADDRESS_BATCH_SIZE = 500
REGULAR_BATCH_SIZE = 50
```

---

## 9. CONTACTS

- **Email**: ngophong4869@gmail.com

---

**Phiên bản**: 2.0  
**Ngày cập nhật**: 7/11/2024
