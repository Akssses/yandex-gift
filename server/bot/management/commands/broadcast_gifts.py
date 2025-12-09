"""
Рассылка подарков всем пользователям из БД с заполненным telegram_id.

Запуск:
    python manage.py broadcast_gifts

Опционально:
    python manage.py broadcast_gifts --delay 0.1  # задержка между сообщениями (сек.)
"""
import time

from django.conf import settings
from django.core.management.base import BaseCommand
from telegram import Bot

from bot.models import TelegramUser


MESSAGE_TEXT = (
    "Привет!\n\n"
    "Мы поправили небольшие технические неполадки — из-за них что-то могло работать некорректно. "
    "Поэтому отправляем сразу два подарка, чтобы всё было удобно и без задержек.\n\n"
    "🎁 Первый подарок — пак аватарок на все случаи жизни: https://disk.360.yandex.ru/d/M5vqMdNsudNk6Q\n\n"
    "Заходи, выбирай и используй!\n\n"
    "🎁 Второй подарок — PDF с идеями, как закастомить рабочее место и поднять себе настроение перед Новым годом:\n"
    "https://disk.360.yandex.ru/i/B9KXT8byngsCig\n\n"
    "Возвращайся завтра за следующим призом!"
)


class Command(BaseCommand):
    help = "Рассылка подарков всем пользователям с telegram_id"

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

        bot = Bot(token=token)
        users = (
            TelegramUser.objects.filter(telegram_id__isnull=False)
            .exclude(telegram_id__exact="")
        )
        total = users.count()
        self.stdout.write(f"Пользователей для рассылки: {total}")

        sent = 0
        errors = 0

        for user in users.iterator():
            try:
                bot.send_message(chat_id=user.telegram_id, text=MESSAGE_TEXT)
                sent += 1
                if delay:
                    time.sleep(delay)
            except Exception as e:
                errors += 1
                self.stderr.write(f"Ошибка для {user.telegram_id}: {e}")

        self.stdout.write(f"Готово. Отправлено: {sent}, ошибок: {errors}")
