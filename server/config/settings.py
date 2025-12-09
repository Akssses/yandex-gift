"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------------------
# 🔐 Security
# ------------------------------------------------------------------------------

SECRET_KEY = 'django-insecure-change-this-in-production'

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    "advent.muza.team",
    "localhost",
    "127.0.0.1",
]
# Убедитесь, что нет wildcards (*) в production

# ------------------------------------------------------------------------------
# Apps
# ------------------------------------------------------------------------------

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'bot',
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'config.middleware.DisableCSRFForAPI',  # должно быть ЗДЕСЬ

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# В режиме DEBUG — используем упрощённый middleware
if DEBUG:
    MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    'config.middleware.DisableCSRFForAPI',  # должно быть ЗДЕСЬ

    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'

# ------------------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------------------

APPEND_SLASH = False  # важно, чтобы Django НЕ создавал сам редиректы 301

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# ------------------------------------------------------------------------------
# Database
# ------------------------------------------------------------------------------

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# ------------------------------------------------------------------------------
# Password validation
# ------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ------------------------------------------------------------------------------
# Localization
# ------------------------------------------------------------------------------

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static files
# ------------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"
# Дополнительно подключаем папку static для сборки
STATICFILES_DIRS = [
    BASE_DIR / "static",
]

# ------------------------------------------------------------------------------
# Telegram bot
# ------------------------------------------------------------------------------

TELEGRAM_BOT_TOKEN = os.environ.get(
    'TELEGRAM_BOT_TOKEN',
    '8574069116:AAGnLh3QmovtnosjfP9ud1A_inxpdlKmQYs'
    # '8584303110:AAESr9bUQUHYKpfYPloLFzHECgaRmRHmzd8'
)

MINI_APP_URL = os.environ.get('MINI_APP_URL', 'https://yandex-gift.vercel.app')

# ------------------------------------------------------------------------------
# CORS
# ------------------------------------------------------------------------------

CORS_ALLOWED_ORIGINS = [
    "https://advent.muza.team",
    "https://yandex-gift.vercel.app",
    "https://adventfront.muza.team",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.vercel\.com$",
]

if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    # В production указываем конкретные домены
    CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

CSRF_TRUSTED_ORIGINS = [
    "https://advent.muza.team",
    "https://yandex-gift.vercel.app",
    "https://adventfront.muza.team",
]

# ------------------------------------------------------------------------------
# HTTPS / Proxy Fix
# ------------------------------------------------------------------------------

# 🔥 ГЛАВНЫЙ ФИКС, КОТОРЫЙ ЛОМАЕТ ВСЕ РЕДИРЕКТЫ ЕСЛИ НЕПРАВИЛЬНЫЙ
# Важно: Django ожидает формат ('HTTP_HEADER_NAME', 'value')
# nginx передает заголовок как X-Forwarded-Proto, Django ищет HTTP_X_FORWARDED_PROTO
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

USE_X_FORWARDED_HOST = True

# В проде Django НЕ должен перенаправлять HTTP -> HTTPS сам
# ЭТО ДЕЛАЕТ nginx, И ТОЛЬКО ОН
SECURE_SSL_REDIRECT = False

# Cookie secure only через HTTPS
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

if DEBUG:
    SECURE_SSL_REDIRECT = False
    CSRF_COOKIE_HTTPONLY = False
