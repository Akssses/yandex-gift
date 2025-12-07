from django.contrib import admin
from .models import TelegramUser, CalendarSettings, GiftOpening


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


@admin.register(CalendarSettings)
class CalendarSettingsAdmin(admin.ModelAdmin):
    list_display = ('current_date', 'updated_at')
    
    def has_add_permission(self, request):
        # Разрешаем только одну запись
        return not CalendarSettings.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(GiftOpening)
class GiftOpeningAdmin(admin.ModelAdmin):
    list_display = ('user', 'day', 'opened_at')
    list_filter = ('day', 'opened_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__telegram_id')
    readonly_fields = ('opened_at',)
    date_hierarchy = 'opened_at'
