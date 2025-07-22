#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的设备控制脚本
用于实际控制设备状态
"""

import json
import hmac
import hashlib
import requests
import time

def control_device(device_id, status, api_key="your-api-key-here"):
    """
    控制设备状态
    
    Args:
        device_id: 设备ID (字符串)
        status: 设备状态 (0=关闭, 1=开启)
        api_key: API密钥
    
    Returns:
        bool: 是否成功
    """
    # 构建请求数据
    request_data = {
        "api_key": api_key,
        "action": "set_status",
        "status": status
    }
    
    # 生成签名
    data_str = json.dumps(request_data, sort_keys=True)
    signature = hmac.new(
        api_key.encode('utf-8'),
        data_str.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    request_data["signature"] = signature
    
    # 发送请求 - 修复URL路径
    url = f"http://127.0.0.1:8001/api/device/{device_id}/control/"#这里要改成自己的服务器ip
    
    try:

        response = requests.post(
            url,
            json=request_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get('success'):
                return True
            else:
                return False
        else:
            return False
            
    except requests.exceptions.RequestException as e:
        return False

def main():

    device_id = "your_device_id"  # 使用实际的设备ID
    
    success = control_device(device_id, 101)#这里写你要设置的状态，1111是全开，1是全关只开主控，也就是说，前面三个1是三个开关。最后一个1是主控。
    

if __name__ == "__main__":
    main() 