"""
Django settings for zhihu_alike project.

Generated by 'django-admin startproject' using Django 1.11.3.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os,sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#添加自定义sys路径
sys.path.insert(0,os.path.join(BASE_DIR,"extra_apps"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '1e(u@v4(1*zsybapo18gg7fge+sz#+7mt)wqd1=^pi1_!8&z=_'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
   # 'channels',
    #'zhihu.apps.ZhihuConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    "captcha",
    "xadmin",
    "crispy_forms",
    'corsheaders',
    'rest_framework',
    'social_django',
    'djcelery',
    'zhihu',
    'django_filters',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',  #注意顺序
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'zhihu_alike.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
            ],
        },
    },
]

WSGI_APPLICATION = 'zhihu_alike.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.getenv('MYSQL_NAME', 'zhihu_alike'),
        'HOST': os.getenv('MYSQL_HOST', 'localhost'),
        'PORT': os.getenv('MYSQL_PORT', '3306'),
        'USER': os.getenv('MYSQL_USER', 'root'),
        'PASSWORD': os.getenv('MYSQL_PASSWORD', '123456'),
        'OPTIONS': {'charset': 'utf8mb4'},
    }
}

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


#APPEND_SLASH=False
AUTH_USER_MODEL = 'zhihu.UserProfile'

#自定义用户登录验证
AUTHENTICATION_BACKENDS = (
    'social_core.backends.weibo.WeiboOAuth2',
    'social_core.backends.qq.QQOAuth2',
    'social_core.backends.github.GithubOAuth2',
    "zhihu.views.CustomAuth",
    'django.contrib.auth.backends.ModelBackend',#这是检测Django用户数据库的基本认证方案。按照 AUTHENTICATION_BACKENDS 的排列顺序，如果同样的用户名和密码在第一次就匹配了，那么Django将停止处理后面的东西。
)


#CORS
#跨域增加忽略
CORS_ALLOW_CREDENTIALS = True
CORS_ORIGIN_ALLOW_ALL = True
CORS_ORIGIN_WHITELIST = (
    '*',
)

CORS_ALLOW_METHODS = (
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
    'VIEW',
)

CORS_ALLOW_HEADERS = (
    'XMLHttpRequest',
    'X_FILENAME',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'Pragma',
)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR,'static'),]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR,'media')

#第三方登录配置
SOCIAL_AUTH_WEIBO_KEY = 'foobar'
SOCIAL_AUTH_WEIBO_SECRET = 'bazqux'

SOCIAL_AUTH_GITHUB_KEY = 'c6a388e7c5cca36b75e4'
SOCIAL_AUTH_GITHUB_SECRET = 'c18384c0f35127bf34b8c897c4d289faf055c471'

#授权成功后跳转页面
SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/index/'


#channels相关配置
#Redis信息
REDIS_OPTIONS = {
    'HOST': '192.168.200.127',
    # 'HOST': '127.0.0.1',
    'PORT': 6379,
    'PASSWD': '123456',
    'DB': 0
}
# #使用Redis作为消息存储，需安装asgi_redis
# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'asgi_redis.RedisChannelLayer',
#         #'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': ['redis://:{0}@{1}:{2}/{3}'.format(REDIS_OPTIONS['PASSWD'], REDIS_OPTIONS['HOST'], REDIS_OPTIONS['PORT'], 1)]
#         },
#
#     }
# }

#缓存：请求的内容缓存中没有就会重新生成
#django-redis缓存 http://django-redis-chs.readthedocs.io/zh_CN/latest/
#密码设置：CONFIG SET requirepass "123456"  ;AUTH 123456
''''测试
python manage.py shell
from django.core.cache import cache
cache.set(key,value,expire)
cache.has_key(key)
cahe.get(key)
'''
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 'redis://:{}@{}:{}/{}'.format( REDIS_OPTIONS['PASSWD'],REDIS_OPTIONS['HOST'], REDIS_OPTIONS['PORT'], 0),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}


'''修改celery4.1.1源码 与 djcelery3.2.2 不兼容之处
celery\bin\base.py line 167 -->option_list = ()
djcelery\management\commands\celery.py line 16 注释掉+base.preload_options

启动：
先启动runserver
然后启动celery:python manage.py celery worker -c 4 --loglevel=info
如果有定时任务：python manage.py celery beat （在/admin中添加，以后研究怎么放到xadmin中）

监控：python manage.py celery flower  （在5555端口查看）
'''
import djcelery
djcelery.setup_loader()
#redis这密码格式真奇怪  调试了半天 一直：Connection error: NOAUTH Authentication required
BROKER_URL= 'redis://:123456@192.168.200.127:6379/0'
CELERY_RESULT_BACKEND = 'redis://:123456@192.168.200.127:6379/0'

# 这样就不用delay了
CELERY_ALWAYS_EAGER = True
#导入任务
CELERY_IMPORTS = ('zhihu.tasks',)
#存储定期任务
CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

# JWT config
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        #一般不能放这作为全局配置 如果token过期的话 不需要验证的页面就不能访问了--放在需要验证的类中
        "rest_framework_jwt.authentication.JSONWebTokenAuthentication",  #解析token，验证用户  请求时带着头：Authorization:JWT token
    )
}


def jwt_response_payload_handler(token, user=None, request=None):
    data = {
        "token": token,
        "username": user.username,
    }
    return data


JWT_AUTH = {
    'JWT_RESPONSE_PAYLOAD_HANDLER': jwt_response_payload_handler,
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=7),
    'JWT_AUTH_HEADER_PREFIX': 'JWT',  #请求头的
}

#drf_extensions
REST_FRAMEWORK_EXTENSIONS = {
"DEFAULT_CACHE_RESPONSE_TIMEOUT":5
}