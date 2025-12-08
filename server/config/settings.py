"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-change-this-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'advent.muza.team,localhost,127.0.0.1').split(',')


# Application definition

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

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'config.middleware.DisableCSRFForAPI',  # Отключаем CSRF для API перед основной проверкой
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# В режиме DEBUG полностью отключаем CSRF проверку для всех запросов
if DEBUG:
    # Заменяем стандартный CSRF middleware на кастомный, который пропускает API
    MIDDLEWARE = [
        'django.middleware.security.SecurityMiddleware',
        'corsheaders.middleware.CorsMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.common.CommonMiddleware',
        'config.middleware.DisableCSRFForAPI',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django.middleware.clickjacking.XFrameOptionsMiddleware',
    ]

ROOT_URLCONF = 'config.urls'

# Отключаем автоматическое добавление слэша для предотвращения 301 редиректов
# Это особенно важно для POST запросов через API
APPEND_SLASH = False

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


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'ru-ru'

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Директория для collectstatic

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Telegram Bot Token
# TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8584303110:AAESr9bUQUHYKpfYPloLFzHECgaRmRHmzd8')
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8574069116:AAGnLh3QmovtnosjfP9ud1A_inxpdlKmQYs')

# Mini App URL
MINI_APP_URL = os.environ.get('MINI_APP_URL', 'https://yandex-gift.vercel.app')

# CORS settings
CORS_ALLOWED_ORIGINS = [
    "https://yandex-gift.vercel.app",
    "https://vercel.app",
    "https://vercel.com",
    "https://advent.muza.team",  # HTTPS только
    "http://localhost:3000",  # Для локальной разработки
    "http://127.0.0.1:3000",  # Для локальной разработки
]

# Разрешаем все домены vercel для разработки
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.vercel\.com$",
]

# В режиме DEBUG разрешаем все источники для упрощения разработки
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True
else:
    CORS_ALLOW_CREDENTIALS = True

CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF trusted origins (для проверки Origin в CSRF)
# Django не поддерживает wildcards, поэтому добавляем конкретные домены
CSRF_TRUSTED_ORIGINS = [
    "https://yandex-gift.vercel.app",
    "https://vercel.app",
    "https://vercel.com",
    "https://advent.muza.team",  # HTTPS только
    "http://localhost:3000",  # Для локальной разработки
    "http://127.0.0.1:3000",  # Для локальной разработки
]

# Настройки безопасности для HTTPS
# Важно: Django работает за nginx прокси, который уже обработал HTTPS
# Поэтому Django должен доверять заголовкам от nginx, а не делать редирект сам
SECURE_SSL_REDIRECT = True  # Редирект HTTP -> HTTPS в production
USE_X_FORWARDED_HOST = True  # Использовать заголовок X-Forwarded-Host от прокси
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Доверять заголовку от nginx
SESSION_COOKIE_SECURE = not DEBUG  # Cookies только по HTTPS в production
CSRF_COOKIE_SECURE = not DEBUG  # CSRF cookies только по HTTPS в production

# В режиме DEBUG отключаем некоторые проверки для разработки
if DEBUG:
    SECURE_SSL_REDIRECT = False  # В DEBUG не делаем редирект
    CSRF_COOKIE_HTTPONLY = False
