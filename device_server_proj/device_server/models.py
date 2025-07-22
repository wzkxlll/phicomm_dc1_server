from django.db import models
import json

# Create your models here.

class Dc1Device(models.Model):
    id = models.CharField(max_length=32, primary_key=True)  # mac或uuid
    status = models.CharField(max_length=8, default="0000")
    I = models.IntegerField(default=0)
    V = models.IntegerField(default=0)
    P = models.IntegerField(default=0)
    update_time = models.BigIntegerField(default=0)
    online = models.BooleanField(default=False)
    power_start_time = models.BigIntegerField(default=0)
    total_power = models.BigIntegerField(default=0)
    names = models.TextField(default="[]")  # 存储JSON数组

    def get_names(self):
        return json.loads(self.names)

    def set_names(self, names_list):
        self.names = json.dumps(names_list)

class DeviceCommand(models.Model):
    id = models.AutoField(primary_key=True)
    device = models.ForeignKey(Dc1Device, on_delete=models.CASCADE)
    command = models.CharField(max_length=8)  # 如"1101"
    status = models.IntegerField(default=0)  # 0未执行，1已执行
    create_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)
