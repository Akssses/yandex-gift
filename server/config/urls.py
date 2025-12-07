"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path
from bot.views import get_calendar_status, open_gift, health_check, check_user

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/health', health_check, name='health_check'),  # Убираем trailing slash для API
    path('api/health/', health_check, name='health_check_slash'),  # Оставляем для совместимости
    path('api/check-user', check_user, name='check_user'),  # Убираем trailing slash для API
    path('api/check-user/', check_user, name='check_user_slash'),  # Оставляем для совместимости
    path('api/calendar/status', get_calendar_status, name='calendar_status'),  # Убираем trailing slash для API
    path('api/calendar/status/', get_calendar_status, name='calendar_status_slash'),  # Оставляем для совместимости
    path('api/calendar/open', open_gift, name='open_gift'),  # Убираем trailing slash для API
    path('api/calendar/open/', open_gift, name='open_gift_slash'),  # Оставляем для совместимости
]
