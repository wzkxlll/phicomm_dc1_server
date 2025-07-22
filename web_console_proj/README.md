# Web Console Project

这是一个基于Django的设备管理Web控制台项目。

## 功能特性

- 设备状态监控
- 远程设备控制
- 实时数据显示
- 用户认证系统

## 安装和配置

### 1. 环境要求

- Python 3.8+
- MySQL 8
- Django 4.2+

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 数据库配置

在 `web_console_proj/settings.py` 中配置数据库连接：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your_database_name',        # 替换为你的数据库名
        'USER': 'your_database_user',        # 替换为你的数据库用户名
        'PASSWORD': 'your_database_password', # 替换为你的数据库密码
        'HOST': 'your_database_host',        # 替换为你的数据库主机地址
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
```

### 4. 其他配置

在 `web_console_proj/settings.py` 中：

1. 设置SECRET_KEY：
```python
SECRET_KEY = 'your-secret-key-here'  # 替换为你的密钥
```

2. 配置ALLOWED_HOSTS：
```python
ALLOWED_HOSTS = ['your-domain.com', 'localhost', '127.0.0.1']  # 添加你的域名
```

### 5. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. 创建超级用户

```bash
python manage.py createsuperuser
```

### 7. 运行开发服务器

```bash
python manage.py runserver 0.0.0.0：8001
```

## 部署

### 使用Gunicorn

1. 修改 `gunicorn_conf.py` 中的路径配置
2. 运行：
```bash
gunicorn -c gunicorn_conf.py web_console_proj.wsgi:application
```

### 使用uWSGI

1. 修改 `uwsgi.ini` 中的路径配置
2. 运行：
```bash
uwsgi --ini uwsgi.ini
```

## 项目结构

```
├── web_console_proj/     # Django项目配置
├── web_console/          # 主应用
├── static/              # 静态文件
├── requirements.txt     # Python依赖
├── gunicorn_conf.py     # Gunicorn配置
├── uwsgi.ini           # uWSGI配置
└── manage.py           # Django管理脚本
```

## 注意事项

- 请确保在生产环境中设置 `DEBUG = False`
- 定期备份数据库
- 使用HTTPS协议保护数据传输
- 定期更新依赖包以修复安全漏洞
