"""
Test server mock for address conversion API
Endpoint: POST /api/convert-batch
"""
from flask import Flask, request, jsonify
import time
import random

app = Flask(__name__)

last_request_time = {}
RATE_LIMIT_SECONDS = 10

TEST_API_KEY = "testing-chuyen-doi-2-cap"

SIMULATE_BALANCE_ERROR = True
BALANCE_ERROR_ADDRESS = "54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng"

MOCK_ADDRESSES_DB = {
    "470 Đ. Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng": "470 Đ. Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng",
    "54 Nguyễn Lương Bằng, Hoà Khánh Bắc, Liên Chiểu, Đà Nẵng": "54 Nguyễn Lương Bằng, Phường Hòa Khánh Bắc, Quận Liên Chiểu, Thành phố Đà Nẵng",
    "470 Trần Đại Nghĩa, Hoà Hải, Ngũ Hành Sơn, Đà Nẵng": "470 Trần Đại Nghĩa, Phường Hòa Hải, Quận Ngũ Hành Sơn, Thành phố Đà Nẵng",
}


@app.route('/api/convert-batch', methods=['POST'])
def convert_batch():
    current_time = time.time()
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            "success": False,
            "error": "Dữ liệu không hợp lệ"
        }), 400
    
    api_key = data.get('key', '')
    addresses = data.get('addresses', [])
    
    if not api_key:
        return jsonify({
            "success": False,
            "error": "API key không được để trống"
        }), 400
    
    if api_key != TEST_API_KEY:
        return jsonify({
            "success": False,
            "error": "API key không hợp lệ"
        }), 401
    
    if not addresses:
        return jsonify({
            "success": False,
            "error": "Danh sách địa chỉ trống"
        }), 400
    
    if len(addresses) > 1000:
        return jsonify({
            "success": False,
            "error": "Chức năng chuyển đổi hàng loạt chỉ hỗ trợ tối đa 1000 địa chỉ/request"
        }), 400
    
    if api_key in last_request_time:
        time_diff = current_time - last_request_time[api_key]
        if time_diff < RATE_LIMIT_SECONDS:
            retry_after = int(RATE_LIMIT_SECONDS - time_diff)
            return jsonify({
                "success": False,
                "error": f"Chức năng chuyển đổi hàng loạt chỉ cho phép 1 lần sử dụng trong {RATE_LIMIT_SECONDS} giây. Vui lòng thử lại sau {retry_after} giây.",
                "rateLimited": True,
                "retryAfter": retry_after
            }), 429
    
    last_request_time[api_key] = current_time
    
    results = []
    successful = 0
    failed = 0
    
    for addr in addresses:
        addr_stripped = addr.strip()
        
        if SIMULATE_BALANCE_ERROR and addr_stripped == BALANCE_ERROR_ADDRESS:
            results.append({
                "original": addr_stripped,
                "converted": "",
                "error": "Số dư không đủ. Cần 150đ, còn lại 0đ",
                "success": False,
                "premium_exchange": False
            })
            failed += 1
        elif addr_stripped in MOCK_ADDRESSES_DB:
            results.append({
                "original": addr_stripped,
                "converted": MOCK_ADDRESSES_DB[addr_stripped],
                "notSure": False,
                "success": True,
                "premium_exchange": random.choice([True, False])
            })
            successful += 1
        else:
            results.append({
                "original": addr_stripped,
                "converted": "",
                "error": "Không tìm thấy địa chỉ tương ứng trong dữ liệu.",
                "success": False,
                "premium_exchange": False
            })
            failed += 1
    
    total_cost = len(addresses) * 50
    
    return jsonify({
        "success": True,
        "data": {
            "total": len(addresses),
            "successful": successful,
            "failed": failed,
            "results": results,
            "totalCost": total_cost,
            "remainingBalance": 100000 - total_cost
        }
    }), 200


@app.route('/api/account-status', methods=['GET'])
def account_status():
    api_key = request.args.get('key', '')
    
    if not api_key:
        return jsonify({
            "success": False,
            "error": "API key không được để trống"
        }), 400
    
    if api_key != TEST_API_KEY:
        return jsonify({
            "success": False,
            "error": "API key không hợp lệ"
        }), 401
    
    return jsonify({
        "success": True,
        "data": {
            "name": "Tài khoản Test",
            "balance": 100000,
            "apiKey": TEST_API_KEY,
            "createdAt": "2024-01-01T10:00:00.000Z",
            "updatedAt": "2025-11-03T08:30:00.000Z"
        }
    }), 200


if __name__ == '__main__':
    print("=" * 60)
    print("Test Server đang chạy tại http://localhost:5000")
    print("API Endpoint: POST http://localhost:5000/api/convert-batch")
    print(f"Test API Key: {TEST_API_KEY}")
    print("=" * 60)
    app.run(host='0.0.0.0', port=5000, debug=True)
