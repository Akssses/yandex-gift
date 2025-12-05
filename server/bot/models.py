from django.db import models


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
