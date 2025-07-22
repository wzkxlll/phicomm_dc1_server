import json
from channels.generic.websocket import AsyncWebsocketConsumer

class DeviceStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        # 可以在此处添加分组逻辑

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        # 这里只做回显，后续会由服务端主动推送设备状态
        if text_data:
            await self.send(text_data=json.dumps({"msg": "pong"}))

    async def send_device_status(self, event):
        await self.send(text_data=json.dumps(event["data"])) 