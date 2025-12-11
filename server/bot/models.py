from django.db import models
from django.utils import timezone


class TelegramUser(models.Model):
    """Модель пользователя Telegram бота"""
    username = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Ник',
        help_text='Ник пользователя в Telegram'
    )
    first_name = models.CharField(
        max_length=255,
        verbose_name='Имя',
        help_text='Имя пользователя'
    )
    last_name = models.CharField(
        max_length=255,
        verbose_name='Фамилия',
        help_text='Фамилия пользователя'
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        null=True,
        blank=True,
        verbose_name='Telegram ID',
        help_text='ID пользователя в Telegram'
    )
    position = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Должность',
        help_text='Текущая должность пользователя'
    )
    is_from_rf = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='Из РФ',
        help_text='Работает ли пользователь с территории РФ'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Пользователь Telegram'
        verbose_name_plural = 'Пользователи Telegram'
        ordering = ['-created_at']

    def __str__(self):
        username_str = f"@{self.username}" if self.username else "без username"
        return f"{self.first_name} {self.last_name} ({username_str})"


class CalendarSettings(models.Model):
    """Настройки календаря - текущая дата для определения доступности подарков"""
    current_date = models.DateField(
        verbose_name='Текущая дата',
        help_text='Установите текущую дату для определения доступности подарков'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Настройка календаря'
        verbose_name_plural = 'Настройки календаря'

    def __str__(self):
        return f"Текущая дата: {self.current_date}"

    @classmethod
    def get_current_date(cls):
        """
        Получить текущую дату из настроек или сегодняшнюю дату.
        Автоматически обновляет значение на сегодняшнюю дату (по Москве),
        чтобы админке не приходилось править дату вручную каждый день.
        """
        today_moscow = timezone.localdate()  # учитывает TIME_ZONE = Europe/Moscow
        settings = cls.objects.first()

        if settings:
            if settings.current_date != today_moscow:
                settings.current_date = today_moscow
                settings.save(update_fields=['current_date', 'updated_at'])
            return settings.current_date

        # Если записи нет, создаём её со значением сегодняшней даты
        settings = cls.objects.create(current_date=today_moscow)
        return settings.current_date


class GiftOpening(models.Model):
    """Отслеживание открытых подарков пользователями"""
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='gift_openings',
        verbose_name='Пользователь'
    )
    day = models.IntegerField(
        verbose_name='День',
        help_text='День декабря (8-19)'
    )
    opened_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата открытия'
    )

    class Meta:
        verbose_name = 'Открытый подарок'
        verbose_name_plural = 'Открытые подарки'
        unique_together = ['user', 'day']
        ordering = ['-opened_at']

    def __str__(self):
        return f"{self.user} - день {self.day} ({self.opened_at.date()})"


class PromoCodeUsage(models.Model):
    """Отслеживание использованных промокодов из резерва"""
    promocode = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Промокод',
        help_text='Использованный промокод из резерва'
    )
    user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='promo_code_usages',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата использования'
    )

    class Meta:
        verbose_name = 'Использованный промокод'
        verbose_name_plural = 'Использованные промокоды'
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.promocode} - {self.user if self.user else 'Unknown'} ({self.used_at.date()})"
