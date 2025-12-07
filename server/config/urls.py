"""
URL configuration for config project.
"""
from django.contrib import admin
from django.urls import path
from bot.views import get_calendar_status, open_gift

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/calendar/status/', get_calendar_status, name='calendar_status'),
    path('api/calendar/open/', open_gift, name='open_gift'),
]
