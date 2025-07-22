import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SECRET_KEY = 'your-secret-key-here'
INSTALLED_APPS = [
    'device_server',
]
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'your-db-name',
        'USER': 'your-db-user',
        'PASSWORD': 'your-db-password',
        'HOST': 'your-db-host',
        'PORT': 'your-db-port',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
} 