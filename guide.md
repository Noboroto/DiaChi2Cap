# API Documentation - Vietnam Address Converter

## 📋 Tổng quan

API Chuyển đổi địa danh Việt Nam cung cấp một bộ công cụ mạnh mẽ để:
1. **Chuẩn hóa và chuyển đổi địa chỉ** đơn lẻ hoặc hàng loạt từ đơn vị hành chính cũ sang mới.
2. **Xác định đơn vị hành chính** (Phường/Xã/Thị trấn) từ tọa độ địa lý (kinh độ, vĩ độ).

Hệ thống được thiết kế để phục vụ các nhà phát triển và doanh nghiệp cần tích hợp chức năng xử lý địa chỉ Việt Nam vào ứng dụng của họ.

---

## 🔑 API Key

### Lấy API Key

Để sử dụng API với hiệu suất cao và không bị giới hạn, bạn cần có API key. Vui lòng liên hệ với chúng tôi qua email **ngophong4869@gmail.com** để được cấp API key và nạp tiền vào tài khoản.

### Sử dụng API Key

Để xác thực, bạn cần gửi API key trong **request body** của mỗi yêu cầu POST.

**Ví dụ:**

```json
{  "key": "your_api_key_here",  // ... các tham số khác}
```

---

## 💰 Bảng giá dịch vụ

Chi phí sẽ được trừ trực tiếp vào số dư tài khoản của bạn cho mỗi yêu cầu thành công.

| Dịch vụ | Mô tả | Đơn giá |
| --- | --- | --- |
| **Chuyển đổi nâng cao** | Chuyển đổi địa chỉ sáp nhập một phần | **150₫** / địa chỉ |

---

## 🚀 API 1: Chuyển đổi địa chỉ

### Endpoint

```
POST https://address-converter.io.vn/api/convert-batch
```

### Mô tả

Chuyển đổi một danh sách địa chỉ cũ sang địa chỉ mới. 

Chi phí thêm được tính toán dựa trên số lượng địa chỉ nâng cao.

### Request Body

```json
{
  "addresses": [
    "Địa chỉ 1, Phường A, Quận B, Tỉnh C",
    "45 Đường X, Phường Y, Quận Z, Tỉnh C"
  ],
  "key": "your_api_key_here"
}
```

**Chi tiết tham số:**

| Tên | Kiểu dữ liệu | Bắt buộc | Mô tả |
| --- | --- | --- | --- |
| `addresses` | `Array<string>` | Có | Mảng chứa các chuỗi địa chỉ cần chuyển đổi. **Giới hạn: 1000 địa chỉ/request**. |
| `key` | `string` | Có | API key của bạn. |

**Định dạng địa chỉ trong mảng `addresses`:**
- `Phường/Xã, Quận/Huyện, Tỉnh/Thành phố`
- `Thôn/Ấp/Số nhà/Đường, Phường/Xã, Quận/Huyện, Tỉnh/Thành phố`

### Response

### Cấu trúc Response thành công

```json
{
  "success": true,
  "data": {
    "total": 2,
    "successful": 2,
    "failed": 0,
    "results": [
      {
        "original": "470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng",
        "converted": "470 Đ. Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng",
        "notSure": false,
        "success": true,
        "premium_exchange": true
      },
      {
        "original": "Địa chỉ không tồn tại, Huyện ABC, Tỉnh XYZ",
        "converted": "",
        "error": "Không tìm thấy địa chỉ tương ứng trong dữ liệu.",
        "success": false,
        "premium_exchange": false
      }
    ],
    "totalCost": 150,
    "remainingBalance": 49850
  }
}
```

**Chi tiết Response:**

| Tên | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `success` | `boolean` | `true` nếu request được xử lý thành công (không có lỗi hệ thống). |
| `data` | `object` | Đối tượng chứa kết quả chi tiết. |
| `data.total` | `number` | Tổng số địa chỉ trong request. |
| `data.successful` | `number` | Số lượng địa chỉ được chuyển đổi thành công. |
| `data.failed` | `number` | Số lượng địa chỉ chuyển đổi thất bại. |
| `data.results` | `Array<object>` | Mảng kết quả, tương ứng với thứ tự địa chỉ đầu vào. |
| `data.results[].original` | `string` | Địa chỉ gốc được gửi lên. |
| `data.results[].converted` | `string` | Địa chỉ mới sau khi chuyển đổi. Sẽ là chuỗi rỗng nếu thất bại. |
| `data.results[].notSure` | `boolean` | `true` nếu hệ thống không chắc chắn 100% về kết quả (ví dụ: một xã cũ được tách thành nhiều xã mới và không có đủ thông tin chi tiết để xác định). |
| `data.results[].success` | `boolean` | `true` nếu địa chỉ này được chuyển đổi thành công. |
|  data.results[].premium_exchange | `boolean` | `true` nếu địa chỉ này được chuyển đổi tốn phí 150đ. |
| `data.results[].error` | `string` | Mô tả lỗi nếu `success` là `false`. |
| `data.totalCost` | `number` | Tổng chi phí cho request này (đơn vị: VNĐ). |
| `data.remainingBalance` | `number` | Số dư còn lại trong tài khoản của bạn sau khi trừ chi phí. |

### Cấu trúc Response lỗi

```json
{  "success": false,  "error": "Mô tả lỗi. Ví dụ: API key không hợp lệ"}
```

---

## 📍 API 2: Chuyển đổi tọa độ

### Endpoint

```
POST https://address-converter.io.vn/api/convert-coordinate
```

### Mô tả

Chuyển đổi một danh sách tọa độ địa lý (kinh độ, vĩ độ) thành thông tin đơn vị hành chính (Phường/Xã/Thị trấn) mới nhất tại vị trí đó.

### Request Body

```json
{
  "coordinates": [
    { "longitude": 108.2022, "latitude": 16.0544 },
    { "longitude": 105.8342, "latitude": 21.0278 }
  ],
  "key": "your_api_key_here"
}
```

**Chi tiết tham số:**

| Tên | Kiểu dữ liệu | Bắt buộc | Mô tả |
| --- | --- | --- | --- |
| `coordinates` | `Array<object>` | Có | Mảng các đối tượng tọa độ. **Giới hạn: 1000 tọa độ/request**. |
| `coordinates[].longitude` | `number` | Có | Kinh độ. |
| `coordinates[].latitude` | `number` | Có | Vĩ độ. |
| `key` | `string` | Có | API key của bạn. |

### Response

### Cấu trúc Response thành công

```json
{
  "success": true,
  "data": [
    {
      "success": true,
      "coordinate": [108.2022, 16.0544],
      "wardInfo": {
        "newWardName": "Phường Hải Châu I",
        "provinceName": "Thành phố Đà Nẵng",
        "wardCode": "20200",
      }
    },
    {
      "success": false,
      "coordinate": [10, 10],
      "error": "Tọa độ không thuộc địa phận Việt Nam"
    }
  ],
  "rateLimitInfo": {
    "remaining": "Infinity",
    "dailyLimit": "Infinity",
    "resetTime": "2024-07-07T17:00:00.000Z"
  }
}
```

**Chi tiết Response:**

| Tên | Kiểu dữ liệu | Mô tả |
| --- | --- | --- |
| `success` | `boolean` | `true` nếu request được xử lý thành công (không có lỗi hệ thống). |
| `data` | `Array<object>` | Mảng chứa kết quả chi tiết cho từng tọa độ, tương ứng với thứ tự đầu vào. |
| `data[].success` | `boolean` | `true` nếu tọa độ này được chuyển đổi thành công. |
| `data[].coordinate` | `Array<number>` | Cặp tọa độ `[longitude, latitude]` đã được xử lý. |
| `data[].wardInfo` | `object` | (Chỉ tồn tại nếu `success` là `true`) Thông tin chi tiết về đơn vị hành chính. |
| `data[].wardInfo.newWardName` | `string` | Tên Phường/Xã/Thị trấn mới. |
| `data[].wardInfo.provinceName` | `string` | Tên Tỉnh/Thành phố. |
| `data[].wardInfo.wardCode` | `string` | Mã Phường/Xã mới. |
| `data[].error` | `string` | (Chỉ tồn tại nếu `success` là `false`) Mô tả lỗi. |

---

## 💼 API 3: Quản lý tài khoản

### Endpoint

```
GET https://address-converter.io.vn/api/account-status?key=your_api_key_here
```

### Mô tả

Kiểm tra thông tin tài khoản và số dư hiện tại.

### Response

```json
{
  "success": true,
  "data": {
    "name": "Tên tài khoản của bạn",
    "balance": 49375,
    "apiKey": "your_api_key_here",
    "createdAt": "2024-07-01T10:00:00.000Z",
    "updatedAt": "2024-07-06T15:30:00.000Z"
  }
}
```

---

## 🚫 Xử lý lỗi

API sử dụng các mã trạng thái HTTP tiêu chuẩn để báo lỗi.

| Mã | Ý nghĩa | Gợi ý xử lý |
| --- | --- | --- |
| `400` | **Bad Request** | Dữ liệu đầu vào không hợp lệ. Kiểm tra lại định dạng `addresses` hoặc `coordinates`. |
| `401` | **Unauthorized** | API key không hợp lệ hoặc bị thiếu. |
| `402` | **Payment Required** | Số dư không đủ để thực hiện yêu cầu. Nạp thêm tiền vào tài khoản. |
| `500` | **Internal Server Error** | Lỗi từ phía server. Vui lòng thử lại sau hoặc liên hệ hỗ trợ. |

---

## 📞 Hỗ trợ

Mọi thắc mắc hoặc cần hỗ trợ kỹ thuật, vui lòng liên hệ qua:
- **Email**: ngophong4869@gmail.com