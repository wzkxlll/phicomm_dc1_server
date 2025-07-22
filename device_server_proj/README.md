# 设备TCP服务端（device_server_proj）

## 启动方法

1. 安装依赖
```
pip install -r requirements.txt
```

2. 启动TCP服务（监听8000端口）
```
python -m device_server/device_tcp_server.py
```


## 说明
- device_server_proj是与DC1连接的服务，它的功能是与dc1保持连接收发命令。
- 与web_console_proj共用同一数据库。 因此两个项目中的数据库配置（在setting.py中,device_server_proj里面有两个setting.py注意都要修改）一定要完全一致。服务检查数据库中的新命令来发送给设备完成控制。
