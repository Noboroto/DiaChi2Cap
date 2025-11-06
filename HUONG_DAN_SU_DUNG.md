# HƯỚNG DẪN SỬ DỤNG - Ứng dụng Chuyển đổi địa chỉ 2 cấp

## DÀNH CHO NGƯỜI DÙNG CUỐI (Công chức Non-IT)

---

## GIỚI THIỆU

Ứng dụng chuyển đổi địa chỉ 2 cấp giúp bạn cập nhật địa chỉ hành chính Việt Nam theo quy định mới nhất. Ứng dụng tự động xử lý hàng nghìn địa chỉ chỉ trong vài phút.

### Điểm nổi bật
- ✅ **Tự động xử lý**: Không cần chỉnh sửa từng địa chỉ
- ✅ **Nhanh chóng**: Xử lý hàng nghìn địa chỉ trong vài phút
- ✅ **Chính xác**: Sử dụng dữ liệu chuẩn từ Bộ Nội vụ
- ✅ **Dễ sử dụng**: Giao diện đơn giản, rõ ràng
- ✅ **Hỗ trợ nhiều định dạng**: Excel (.xlsx) và Text (.txt)

---

## CÁCH SỬ DỤNG ỨNG DỤNG

### Bước 1: Khởi động ứng dụng

1. Nhấp đúp vào file `ChuyenDoiDiaChi.exe`
2. Ứng dụng sẽ mở ra với giao diện màu xanh

### Bước 2: Nhập mã API

1. Tìm ô "API Key" ở đầu ứng dụng
2. Dán mã API của bạn vào ô này
3. Ứng dụng sẽ tự động kiểm tra và hiển thị thông tin tài khoản:
   - Tình trạng tài khoản
   - Số dư còn lại
   - Ngày tạo tài khoản

**Lưu ý**: Nếu chưa có API Key, liên hệ: ngophong4869@gmail.com

### Bước 3: Chọn file cần chuyển đổi

1. Nhấn nút "Chọn file"
2. Tìm file địa chỉ của bạn (hỗ trợ .txt hoặc .xlsx)
3. Nhấn "Mở"

### Bước 4: Bắt đầu chuyển đổi

1. Nhấn nút "CHUYỂN ĐỔI" màu xanh
2. Theo dõi tiến trình xử lý trên thanh tiến độ
3. Đọc kết quả chi tiết ở ô bên dưới

### Bước 5: Xem kết quả

1. Sau khi hoàn thành, nhấn nút "MỞ THƯ MỤC KẾT QUẢ"
2. File kết quả sẽ có tên: `{tên_file_gốc}_converted.{txt|xlsx}`
3. Mở file này để xem địa chỉ đã chuyển đổi

---

## ĐỊNH DẠNG FILE ĐẦU VÀO

### Cách 1: File Text (.txt) - Địa chỉ đầy đủ

Mỗi dòng là một địa chỉ hoàn chỉnh:

```
Phường Bến Nghé, Quận 1, TP HCM
123 Lê Lợi, Phường Bến Thành, Quận 1, TP HCM
Xã Tân Phú, Huyện Củ Chi, TP HCM
```

### Cách 2: File Text (.txt) - Nhiều cột

Dữ liệu phân tách bằng dấu | (pipe):

```
so_nha_duong|phuong_xa|quan_huyen|tinh_thanh
123 Lê Lợi|Phường Bến Thành|Quận 1|TP HCM
|Phường Bến Nghé|Quận 1|TP HCM
45 Nguyễn Huệ|Phường Bến Nghé|Quận 1|TP HCM
```

### Cách 3: File Excel (.xlsx)

| A (so_nha_duong) | B (phuong_xa) | C (quan_huyen) | D (tinh_thanh) |
|------------------|---------------|----------------|----------------|
| 123 Lê Lợi | Phường Bến Thành | Quận 1 | TP HCM |
| | Phường Bến Nghé | Quận 1 | TP HCM |
| 45 Nguyễn Huệ | Phường Bến Nghé | Quận 1 | TP HCM |

---

## HIỂU KẾT QUẢ CHUYỂN ĐỔI

### Trường hợp thành công

Ứng dụng hiển thị:
```
Phường Bến Nghé, Quận 1, TP HCM
→ Phường Bến Nghé, Quận 1, Thành phố Hồ Chí Minh
```

**Ý nghĩa**: Địa chỉ đã được cập nhật theo quy định mới

### File kết quả với nhiều cột

Nếu file đầu vào có nhiều cột, kết quả sẽ bao gồm:
- Tất cả các cột gốc
- **Số lần thử**: Số lần ứng dụng thử gửi yêu cầu (thường là 1)
- **Mã phường/xã mới**: Mã số hành chính của phường/xã (tự động trích xuất)
- **Phường/Xã mới**: Tên phường/xã sau khi chuyển đổi
- **Mã tỉnh/thành mới**: Mã số hành chính của tỉnh/thành (tự động trích xuất)
- **Tỉnh/Thành mới**: Tên tỉnh/thành sau khi chuyển đổi

**Ví dụ**:
```
| Mã | Số nhà/Đường | Phường/Xã cũ | ... | Mã phường mới | Phường mới | Mã tỉnh mới | Tỉnh mới |
| 001 | 123 Lê Lợi | Bến Thành | ... | 268 | Phường Bến Thành | 12 | TP Hồ Chí Minh |
```

**Lợi ích của mã hành chính**:
- Dễ dàng tra cứu và đối chiếu với cơ sở dữ liệu quốc gia
- Tích hợp với các hệ thống khác
- Chuẩn hóa dữ liệu địa chỉ

### Trường hợp lỗi

Ứng dụng hiển thị:
```
LỖI: Không tìm thấy địa chỉ tương ứng trong dữ liệu
```

**Nguyên nhân có thể**:
- Địa chỉ viết sai chính tả
- Địa chỉ không tồn tại trong cơ sở dữ liệu
- Thiếu thông tin quan trọng (phường/xã, quận/huyện, tỉnh/thành)

**Cách xử lý**:
1. Kiểm tra lại địa chỉ gốc
2. Bổ sung thông tin còn thiếu
3. Thử lại với địa chỉ đã sửa

---

## CÁC TÌNH HUỐNG THƯỜNG GẶP

### 1. Ứng dụng báo "Số dư không đủ"

**Nguyên nhân**: Tài khoản API đã hết số dư

**Cách xử lý**:
- Nạp thêm tiền vào tài khoản
- Liên hệ: ngophong4869@gmail.com để được hỗ trợ

### 2. Ứng dụng báo "Đang chờ..."

**Nguyên nhân**: Hệ thống đang xử lý nhiều yêu cầu cùng lúc

**Cách xử lý**:
- Chờ thời gian hiển thị trên màn hình
- Ứng dụng sẽ tự động tiếp tục

### 3. Muốn dừng giữa chừng

1. Nhấn nút "DỪNG" màu đỏ
2. Ứng dụng sẽ lưu kết quả đã xử lý
3. Các địa chỉ chưa xử lý sẽ được đánh dấu

### 4. File kết quả bị lỗi tiếng Việt

**Nguyên nhân**: Excel mở không đúng mã hóa UTF-8

**Cách xử lý**:
1. Mở Excel → Data → Get Data → From Text/CSV
2. Chọn file kết quả
3. Chọn encoding: UTF-8
4. Click "Load"

---

## CÁC LƯU Ý QUAN TRỌNG

### Về dữ liệu đầu vào

✅ **Nên**:
- Sử dụng địa chỉ đầy đủ, rõ ràng
- Kiểm tra chính tả trước khi chuyển đổi
- Sử dụng định dạng chuẩn (Phường/Xã, Quận/Huyện, Tỉnh/Thành)

❌ **Không nên**:
- Viết tắt quá nhiều (P. 1 thay vì Phường 1)
- Thiếu thông tin hành chính cơ bản
- Dùng địa chỉ cũ đã không còn tồn tại

### Về hiệu suất

- **File nhỏ** (< 1000 địa chỉ): Xử lý trong vài giây
- **File vừa** (1000-5000 địa chỉ): Xử lý khoảng 1-2 phút
- **File lớn** (> 5000 địa chỉ): Có thể mất 5-10 phút

### Về API Key

- Mỗi API Key chỉ dùng cho 1 tài khoản
- Không chia sẻ API Key cho người khác
- Liên hệ ngay nếu API Key bị lộ

---

## XỬ LÝ LỖI THƯỜNG GẶP

### Lỗi: "Không thể mở file"

**Nguyên nhân**: File đang được mở bởi chương trình khác

**Cách xử lý**:
1. Đóng tất cả Excel/Notepad
2. Thử lại

### Lỗi: "Không kết nối được server"

**Nguyên nhân**: Mất kết nối Internet

**Cách xử lý**:
1. Kiểm tra kết nối Internet
2. Thử ping google.com
3. Khởi động lại ứng dụng

### Lỗi: "File không đúng định dạng"

**Nguyên nhân**: File không phải .txt hoặc .xlsx

**Cách xử lý**:
1. Kiểm tra đuôi file
2. Chuyển đổi sang đúng định dạng
3. Thử lại

---

## CÂU HỎI THƯỜNG GẶP (FAQ)

**Hỏi: Ứng dụng có cần Internet không?**
Đáp: Có, ứng dụng cần Internet để kết nối đến server xử lý.

**Hỏi: Dữ liệu của tôi có bị lưu trữ không?**
Đáp: Không, mọi dữ liệu chỉ xử lý tạm thời và không được lưu trữ.

**Hỏi: Kết quả có chính xác 100% không?**
Đáp: Kết quả dựa trên cơ sở dữ liệu chính thức của Bộ Nội vụ, độ chính xác > 95%.

**Hỏi: Tôi có thể chạy nhiều file cùng lúc không?**
Đáp: Không, chỉ xử lý 1 file tại 1 thời điểm.

**Hỏi: File kết quả lưu ở đâu?**
Đáp: Trong thư mục `output` cùng thư mục với ứng dụng.

---

## LIÊN HỆ HỖ TRỢ

### Khi nào cần liên hệ?

- Không thể đăng nhập hoặc sử dụng API Key
- Kết quả chuyển đổi không chính xác
- Gặp lỗi không thể tự xử lý
- Cần hướng dẫn chi tiết hơn

### Thông tin liên hệ

**Email**: ngophong4869@gmail.com

**Nội dung email nên bao gồm**:
1. Mô tả vấn đề gặp phải
2. Ảnh chụp màn hình (nếu có)
3. File dữ liệu mẫu (nếu cần)
4. API Key của bạn (để kiểm tra)

**Thời gian phản hồi**: Trong vòng 24 giờ làm việc

---

## PHỤ LỤC

### Danh sách viết tắt được chấp nhận

| Viết tắt | Đầy đủ |
|----------|---------|
| TP | Thành phố |
| TX | Thị xã |
| TT | Thị trấn |
| Q. | Quận |
| H. | Huyện |
| P. | Phường |
| X. | Xã |

---

**Phiên bản hướng dẫn**: 2.0  
**Ngày cập nhật**: 7 tháng 11, 2024  
**Dành cho**: Người dùng cuối - Công chức Non-IT

---

## KẾT LUẬN

Ứng dụng Chuyển đổi địa chỉ 2 cấp được thiết kế để giúp bạn tiết kiệm thời gian và công sức trong việc cập nhật địa chỉ hành chính. Hãy làm theo hướng dẫn trên để đạt kết quả tốt nhất.

Nếu có bất kỳ thắc mắc nào, đừng ngần ngại liên hệ với chúng tôi qua email: ngophong4869@gmail.com

**Chúc bạn sử dụng thành công!**
