Base: https://address-converter.io.vn/
API 1: Chuyển đổi địa chỉ
Endpoint
POST /api/convert-batch
Hỗ trợ tối đa 1000 địa chỉ/request
Request Body
```json
{
  "addresses": [
    "470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng",
    "54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng"
  ],
  "key": "your_api_key_here"
}
```
Response
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
        "original": "54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng",
        "converted": "54 Nguyễn Lương Bằng, Phường Hòa Khánh Bắc, Quận Liên Chiểu, Thành phố Đà Nẵng",
        "notSure": false,
        "success": true,
        "premium_exchange": false
      }
    ],
    "totalCost": 150,
    "remainingBalance": 99850
  }
}
```
Hoặc
```json
{
    "success": false,
    "error": "Chức năng chuyển đổi hàng loạt chỉ cho phép 1 lần sử dụng trong 5 phút. Vui lòng thử lại sau 21 giây.",
    "rateLimited": true,
    "retryAfter": 21
}
```
Hoặc 

```json
{
    "success": true,
    "data": {
        "total": 3,
        "successful": 1,
        "failed": 2,
        "results": [
            {
                "original": "456 đường Lương Định Của, Phường An Khánh, Quận 2, TP. Hồ Chí Minh.",
                "converted": "",
                "error": "Không tìm thấy địa chỉ tương ứng trong dữ liệu.",
                "success": false,
                "premium_exchange": false
            },
            {
                "original": "123 đường Man Thiện, Phường Tăng Nhơn Phú A, Quận 9, TP. Hồ Chí Minh.",
                "converted": "",
                "error": "Không tìm thấy địa chỉ tương ứng trong dữ liệu.",
                "success": false,
                "premium_exchange": false
            },
            {
                "original": "54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng",
                "converted": "54 Nguyễn Lương Bằng, Phường Liên Chiểu, Thành phố Đà Nẵng",
                "notSure": false,
                "success": true,
                "premium_exchange": false
            }
        ]
    }
}
```