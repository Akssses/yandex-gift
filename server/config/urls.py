"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path
from bot.views import get_calendar_status, open_gift, health_check, check_user

urlpatterns = [
    path('admin/', admin.site.urls),
    # API endpoints без trailing slash (APPEND_SLASH = False)
    path('api/health', health_check, name='health_check'),
    path('api/check-user', check_user, name='check_user'),
    path('api/calendar/status', get_calendar_status, name='calendar_status'),
    path('api/calendar/open', open_gift, name='open_gift'),
]
