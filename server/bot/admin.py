from django.contrib import admin
from .models import TelegramUser, CalendarSettings, GiftOpening, PromoCodeUsage, FutureLetter


class GiftOpeningInline(admin.TabularInline):
    model = GiftOpening
    extra = 0
    readonly_fields = ('day', 'opened_at')
    can_delete = False


class FutureLetterInline(admin.StackedInline):
    model = FutureLetter
    extra = 0
    can_delete = False
    readonly_fields = ("text", "created_at", "send_at", "sent_at")
    fields = ("text", "created_at", "send_at", "sent_at")


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'telegram_id',
        'stack_display',
        'country_display',
        'city_display',
        'opened_days_display',
        'is_waiting_future_letter',
        'future_letter_requested_at',
        'future_letter_received_at',
        'created_at',
    )
    list_filter = ('is_from_rf', 'is_waiting_future_letter', 'created_at')
    search_fields = ('username', 'first_name', 'last_name', 'telegram_id')
    readonly_fields = (
        'telegram_id',
        'created_at',
        'updated_at',
        'opened_days_display',
        'stack_display',
        'country_display',
        'city_display',
        'future_letter_requested_at',
        'future_letter_received_at',
    )
    inlines = [GiftOpeningInline, FutureLetterInline]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'first_name', 'last_name')
        }),
        ('Telegram данные', {
            'fields': (
                'telegram_id',
                'position',
                'is_from_rf',
                'stack_display',
                'country_display',
                'city_display',
                'opened_days_display',
            )
        }),
        ('Письмо в будущее', {
            'fields': (
                'is_waiting_future_letter',
                'future_letter_requested_at',
                'future_letter_received_at',
            ),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    # ----- helpers -----
    def stack_display(self, obj):
        return obj.position or "—"
    stack_display.short_description = "Стек"

    def country_display(self, obj):
        if obj.is_from_rf is None:
            return "—"
        return "Россия" if obj.is_from_rf else "Другая страна"
    country_display.short_description = "Страна"

    def city_display(self, obj):
        # Отдельного поля нет, поэтому показываем placeholder
        return "—"
    city_display.short_description = "Город"

    def opened_days_display(self, obj):
        days = obj.gift_openings.values_list('day', flat=True).order_by('day')
        return ", ".join(str(d) for d in days) if days else "—"
    opened_days_display.short_description = "Открытые дни"


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


@admin.register(PromoCodeUsage)
class PromoCodeUsageAdmin(admin.ModelAdmin):
    list_display = ('promocode', 'user', 'used_at')
    list_filter = ('used_at',)
    search_fields = ('promocode', 'user__username', 'user__first_name', 'user__last_name', 'user__telegram_id')
    readonly_fields = ('used_at',)
    date_hierarchy = 'used_at'


@admin.register(FutureLetter)
class FutureLetterAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "send_at", "sent_at")
    list_filter = ("sent_at", "created_at", "send_at")
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__telegram_id", "text")
    readonly_fields = ("created_at", "sent_at")
    date_hierarchy = "created_at"
