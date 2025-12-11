"""
Ежедневное напоминание о новом подарке с кнопкой открытия мини-аппа.

Запуск вручную:
    python manage.py send_daily_reminder

Рекомендуемый cron (11:00 по Москве, если системный TZ=Europe/Moscow):
    0 11 * * * /path/to/venv/bin/python /path/to/manage.py send_daily_reminder >> /var/log/send_daily_reminder.log 2>&1
"""
import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo

from bot.models import TelegramUser


MESSAGE_TEXT = "Новый подарок уже доступен — не забудь его забрать до конца дня 🌟"


class Command(BaseCommand):
    help = "Ежедневное напоминание о новом подарке с кнопкой мини-аппа"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delay",
            type=float,
            default=0.05,
            help="Задержка между сообщениями в секундах (по умолчанию 0.05)",
        )

    def handle(self, *args, **options):
        delay = options["delay"]
        token = settings.TELEGRAM_BOT_TOKEN

        if not token:
            self.stderr.write("TELEGRAM_BOT_TOKEN не задан в настройках.")
            return

        app_url = getattr(settings, "MINI_APP_URL", "").strip()
        if not app_url:
            self.stderr.write("MINI_APP_URL не задан в settings.py.")
            return

        users = list(
            TelegramUser.objects.filter(
                telegram_id__isnull=False,
                telegram_id__gt=0,
            )
        )
        total = len(users)
        self.stdout.write(f"Пользователей для рассылки: {total}")

        sent = 0
        errors = 0

        async def send_all():
            nonlocal sent, errors
            bot = Bot(token=token)
            markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="Открыть календарь",
                            web_app=WebAppInfo(url=app_url),
                        )
                    ]
                ]
            )
            for user in users:
                try:
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=MESSAGE_TEXT,
                        reply_markup=markup,
                    )
                    sent += 1
                    if delay:
                        await asyncio.sleep(delay)
                except Exception as e:
                    errors += 1
                    self.stderr.write(f"Ошибка для {user.telegram_id}: {e}")

        asyncio.run(send_all())
        self.stdout.write(f"Готово. Отправлено: {sent}, ошибок: {errors}")
