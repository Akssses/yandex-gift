"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path
from bot.views import get_calendar_status, open_gift, health_check, check_user

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints - добавляем оба варианта (с trailing slash и без) для совместимости
    path('api/health', health_check, name='health_check'),
    path('api/health/', health_check, name='health_check_slash'),
    path('api/check-user', check_user, name='check_user'),
    path('api/check-user/', check_user, name='check_user_slash'),
    path('api/calendar/status', get_calendar_status, name='calendar_status'),
    path('api/calendar/status/', get_calendar_status, name='calendar_status_slash'),
    path('api/calendar/open', open_gift, name='open_gift'),
    path('api/calendar/open/', open_gift, name='open_gift_slash'),
]
