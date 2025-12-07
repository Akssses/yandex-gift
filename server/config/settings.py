"""
Django settings for config project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv

# ============================================================
# LOAD ENV
# ============================================================

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-me')

DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    "advent.muza.team",
    "www.advent.muza.team",
]

# Разрешаем всё для удобства API
if DEBUG:
    ALLOWED_HOSTS.append("*")


# ============================================================
# APPS
# ============================================================

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party
    'corsheaders',

    # Local apps
    'bot',
]


# ============================================================
# MIDDLEWARE (ВАЖНО: порядок CORS!)
# ============================================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',

    # CORS ДОЛЖЕН быть выше SessionMiddleware и CommonMiddleware
    'corsheaders.middleware.CorsMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # отключение CSRF для API (твоя кастомка)
    'config.middleware.DisableCSRFForAPI',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# ============================================================
# URLS + WSGI
# ============================================================

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'


# ============================================================
# DATABASE
# ============================================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ============================================================
# I18N
# ============================================================

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True


# ============================================================
# STATIC
# ============================================================

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# ============================================================
# TELEGRAM BOT CONFIG
# ============================================================

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
MINI_APP_URL = os.environ.get("MINI_APP_URL", "https://yandex-gift.vercel.app")


# ============================================================
# CORS — <РАБОТАЕТ БЕЗОТКАЗНО> 🔥
# ============================================================

# Разрешаем ВСЕ домены (API friendly)
CORS_ALLOW_ALL_ORIGINS = True

# Разрешаем куки, если вдруг понадобятся
CORS_ALLOW_CREDENTIALS = True

# Разрешаем любые методы
CORS_ALLOW_METHODS = [
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
]

# Разрешаем любые заголовки
CORS_ALLOW_HEADERS = [
    "*",
]

# Разрешаем все домены Vercel (твои mini-appы)
CORS_ALLOWED_ORIGIN_REGEXES = [
    r"^https://.*\.vercel\.app$",
    r"^https://.*\.vercel\.com$",
]


# ============================================================
# CSRF — ПОЛНОСТЬЮ ОТКЛЮЧЕН ДЛЯ API
# ============================================================

CSRF_TRUSTED_ORIGINS = [
    "https://advent.muza.team",
    "https://yandex-gift.vercel.app",
    "https://*.vercel.app",
]

# Если DEBUG — отключаем secure cookies
if DEBUG:
    CSRF_COOKIE_SECURE = False
    CSRF_COOKIE_HTTPONLY = False
