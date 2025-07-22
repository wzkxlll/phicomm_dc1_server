import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
import django
django.setup()
import asyncio
import json
from device_server.models import Dc1Device, DeviceCommand
from django.utils import timezone
from asgiref.sync import sync_to_async

DEVICE_PORT = 8000

# 数据库操作全部用sync_to_async包装
@sync_to_async
def get_device(device_id):
    try:
        return Dc1Device.objects.get(id=device_id)
    except Dc1Device.DoesNotExist:
        return None

@sync_to_async
def create_or_update_device(device_id, **kwargs):
    obj, created = Dc1Device.objects.get_or_create(id=device_id, defaults=kwargs)
    if not created:
        for k, v in kwargs.items():
            setattr(obj, k, v)
        obj.save()
    return obj

@sync_to_async
def update_device_status(device_id, status, I, V, P):
    obj, _ = Dc1Device.objects.get_or_create(id=device_id)
    obj.status = status
    obj.I = I
    obj.V = V
    obj.P = P
    obj.update_time = int(timezone.now().timestamp() * 1000)
    obj.online = True
    obj.save()
    return obj

@sync_to_async
def set_device_offline(device_id):
    try:
        obj = Dc1Device.objects.get(id=device_id)
        obj.online = False
        obj.save()
    except Dc1Device.DoesNotExist:
        pass

@sync_to_async
def get_pending_command(device_id):
    cmds = DeviceCommand.objects.filter(device_id=device_id, status=0).order_by('create_time')
    if cmds.exists():
        return cmds.first()
    return None

@sync_to_async
def mark_command_done(cmd_id):
    DeviceCommand.objects.filter(id=cmd_id).update(status=1)

@sync_to_async
def get_latest_pending_command(device_id):
    cmds = DeviceCommand.objects.filter(device_id=device_id, status=0).order_by('-create_time')
    if cmds.exists():
        return cmds.first()
    return None

@sync_to_async
def mark_all_pending_done(device_id):
    DeviceCommand.objects.filter(device_id=device_id, status=0).update(status=1)

class DeviceSession:
    def __init__(self, reader, writer):
        self.reader = reader
        self.writer = writer
        self.device_id = None
        self.last_active = timezone.now()
        self.query_task = None
        self.check_cmd_task = None

    async def handle(self):
        try:
            while True:
                data = await self.reader.readline()
                if not data:
                    break
                msg = data.decode().strip()
                if not msg:
                    continue
                print(f"[设备->服务器] 收到: {msg}")
                await self.process_message(msg)
                self.last_active = timezone.now()
        except Exception as e:
            pass
        finally:
            if self.device_id:
                await set_device_offline(self.device_id)
            if self.query_task:
                self.query_task.cancel()
            if self.check_cmd_task:
                self.check_cmd_task.cancel()
            self.writer.close()
            await self.writer.wait_closed()

    async def process_message(self, msg):
        try:
            data = json.loads(msg)
        except Exception:
            return
        action = data.get('action')
        if action == 'activate=':
            params = data.get('params', {})
            mac = params.get('mac')
            self.device_id = mac
            await create_or_update_device(mac, online=True)
            self.query_task = asyncio.create_task(self.periodic_query())
            self.check_cmd_task = asyncio.create_task(self.periodic_check_command())
        elif action == 'identify':
            params = data.get('params', {})
            device_id = params.get('device_id')
            self.device_id = device_id
            await create_or_update_device(device_id, online=True)
            resp = {
                'uuid': data.get('uuid'),
                'status': 200,
                'result': {},
                'msg': 'device identified'
            }
            await self.send_json(resp)
            self.query_task = asyncio.create_task(self.periodic_query())
            self.check_cmd_task = asyncio.create_task(self.periodic_check_command())
        elif action == 'kWh+':
            # 用电量上报
            detal_kwh = int(data.get('params', {}).get('detalKWh', 0))
            if self.device_id and detal_kwh > 0:
                obj = await get_device(self.device_id)
                if obj:
                    if obj.power_start_time == 0:
                        obj.power_start_time = int(timezone.now().timestamp() * 1000)
                        obj.total_power = 0
                    else:
                        obj.total_power += detal_kwh
                    obj.save()
        elif action == 'datapoint':
            # 设备状态查询请求，回复当前设备状态
            if self.device_id:
                obj = await get_device(self.device_id)
                if obj:
                    resp = {
                        'uuid': data.get('uuid'),
                        'status': 200,
                        'result': {
                            'status': int(obj.status),
                            'I': obj.I,
                            'V': obj.V,
                            'P': obj.P
                        },
                        'msg': 'datapoint result'
                    }
                    await self.send_json(resp)
        elif action == 'datapoint=':
            # 设置开关
            params = data.get('params', {})
            status = params.get('status')
            if self.device_id and status is not None:
                obj = await get_device(self.device_id)
                if obj:
                    obj.status = str(status)
                    obj.save()
                    resp = {
                        'uuid': data.get('uuid'),
                        'status': 200,
                        'result': {'status': int(obj.status)},
                        'msg': 'set status ok'
                    }
                    await self.send_json(resp)
        # 设备状态上报
        if 'result' in data and self.device_id:
            result = data['result']
            status = str(result.get('status', '0000'))
            I = int(result.get('I', 0))
            V = int(result.get('V', 0))
            P = int(result.get('P', 0))
            await update_device_status(self.device_id, status, I, V, P)

    async def send_json(self, obj):
        if 'params' in obj and 'status' in obj['params']:
            print(f"[DEBUG] send_json status类型: {type(obj['params']['status'])}, 值: {obj['params']['status']}")
        msg = json.dumps(obj) + '\n'
        print(f"[服务器->设备] 发送: {msg.strip()}")
        self.writer.write(msg.encode())
        await self.writer.drain()

    async def periodic_query(self):
        while True:
            await asyncio.sleep(5)
            if self.device_id:
                uuid = f"T{int(timezone.now().timestamp()*1000)}"
                query = {
                    'action': 'datapoint',
                    'uuid': uuid,
                    'auth': '',
                    'params': ''
                }
                await self.send_json(query)

    async def periodic_check_command(self):
        while True:
            await asyncio.sleep(1)
            if self.device_id:
                cmd = await get_latest_pending_command(self.device_id)
                if cmd:
                    uuid = f"T{int(timezone.now().timestamp()*1000)}"
                    try:
                        status_int = int(cmd.command, 10)
                    except Exception:
                        status_int = 0
                    print(f"[DEBUG] 下发前 status_int类型: {type(status_int)}, 值: {status_int}")
                    set_cmd = {
                        'action': 'datapoint=',
                        'uuid': uuid,
                        'auth': '',
                        'params': {'status': status_int}
                    }
                    await self.send_json(set_cmd)
                    await mark_all_pending_done(self.device_id)

async def start_device_server():
    server = await asyncio.start_server(
        lambda r, w: DeviceSession(r, w).handle(),
        '0.0.0.0', DEVICE_PORT
    )
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    import asyncio
    asyncio.run(start_device_server()) 