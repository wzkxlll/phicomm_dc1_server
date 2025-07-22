from django.shortcuts import render, get_object_or_404, redirect
from .models import Dc1Device, DeviceCommand
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
import json
import hashlib
import hmac
import base64
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# 设备列表页面
@login_required
def device_list(request):
    devices = Dc1Device.objects.all()
    # 构造json_data，确保online字段为数据库最新状态
    json_data = json.dumps([
        {
            'id': d.id,
            'status': d.status,
            'I': d.I,
            'V': d.V,
            'P': d.P,
            'total_power': d.total_power,
            'names': d.get_names(),
            'online': d.online
        } for d in devices
    ], ensure_ascii=False)
    return render(request, 'web_console/device_list.html', {'devices': devices, 'json_data': json_data})

# 设备详情页面
@login_required
def device_detail(request, device_id):
    device = get_object_or_404(Dc1Device, id=device_id)
    vue_data = {
        'status': device.status,
        'I': device.I,
        'V': device.V,
        'P': device.P,
        'total_power': device.total_power,
        'online': device.online,
        'names': device.get_names(),
    }
    return render(request, 'web_console/device_detail.html', {'device': device, 'vue_data': json.dumps(vue_data, ensure_ascii=False)})

# 设备开关控制API
@csrf_exempt
@login_required
def set_device_status(request, device_id):
    if request.method == 'POST':
        status = request.POST.get('status')
        device = get_object_or_404(Dc1Device, id=device_id)
        try:
            status_int = int(status)
        except Exception:
            status_int = 0
        DeviceCommand.objects.create(device=device, command=str(status_int))
        return JsonResponse({'result': 'ok'})
    return JsonResponse({'result': 'fail'}, status=400)

# 预定义的密钥列表
API_KEYS = [
    "kdj_device_control_2024_key1",
    "kdj_device_control_2024_key2", 
    "kdj_device_control_2024_key3"
]

def verify_api_key(request_data, signature, api_key):
    """
    验证API密钥
    使用HMAC-SHA256进行签名验证
    """
    try:
        # 剔除 signature 字段
        data_to_sign = {k: v for k, v in request_data.items() if k != "signature"}
        data_str = json.dumps(data_to_sign, sort_keys=True)
        expected_signature = hmac.new(
            api_key.encode('utf-8'),
            data_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature == expected_signature
    except Exception as e:
        print(f"[API认证] 签名验证异常: {e}")
        return False

@csrf_exempt
@require_http_methods(["POST"])
def api_control_device(request, device_id):
    """
    API设备控制接口
    使用密钥认证，接受POST请求控制设备状态
    """
    print(f"[API请求] 设备控制接口: 设备ID={device_id}")
    
    try:
        # 解析请求数据
        request_data = json.loads(request.body.decode('utf-8'))
        print(f"[API请求] 请求数据: {request_data}")
        
        # 获取认证信息
        api_key = request_data.get('api_key')
        signature = request_data.get('signature')
        action = request_data.get('action')
        status = request_data.get('status')
        
        print(f"[API认证] API Key: {api_key}")
        print(f"[API认证] 签名: {signature}")
        print(f"[API认证] 动作: {action}")
        print(f"[API认证] 状态: {status}")
        
        # 验证API密钥是否在允许列表中
        if api_key not in API_KEYS:
            print(f"[API认证] 无效的API密钥: {api_key}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid API key'
            }, status=401)
        
        # 验证签名
        if not verify_api_key(request_data, signature, api_key):
            print(f"[API认证] 签名验证失败")
            return JsonResponse({
                'success': False,
                'error': 'Invalid signature'
            }, status=401)
        
        # 获取设备
        try:
            device = Dc1Device.objects.get(id=device_id)
        except Dc1Device.DoesNotExist:
            print(f"[API认证] 设备不存在: {device_id}")
            return JsonResponse({
                'success': False,
                'error': 'Device not found'
            }, status=404)
        
        # 执行设备控制
        if action == 'set_status':
            try:
                status_int = int(status)
                # 创建设备命令
                DeviceCommand.objects.create(device=device, command=str(status_int))
                print(f"[API响应] 设备控制成功: 设备ID={device_id}, status={status_int}")
                return JsonResponse({
                    'success': True,
                    'message': f'Device {device_id} status set to {status_int}',
                    'device_id': device_id,
                    'status': status_int
                })
            except (ValueError, TypeError):
                print(f"[API响应] 状态值无效: {status}")
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid status value'
                }, status=400)
        else:
            print(f"[API响应] 无效的动作: {action}")
            return JsonResponse({
                'success': False,
                'error': 'Invalid action'
            }, status=400)
            
    except json.JSONDecodeError:
        print(f"[API请求] JSON解析失败")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        print(f"[API请求] 异常: {e}")
        return JsonResponse({
            'success': False,
            'error': 'Internal server error'
        }, status=500)

