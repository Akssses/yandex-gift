from django.contrib import admin
from .models import TelegramUser


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'first_name', 'last_name', 'telegram_id', 'is_from_rf', 'created_at')
    list_filter = ('is_from_rf', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'telegram_id')
    readonly_fields = ('telegram_id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Telegram данные', {
            'fields': ('telegram_id', 'position', 'is_from_rf')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
