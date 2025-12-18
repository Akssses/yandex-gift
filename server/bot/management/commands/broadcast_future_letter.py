"""
Рассылка: просьба написать письмо себе в будущее.

Запуск:
    python manage.py broadcast_future_letter

Опции:
    --delay 0.05   # задержка между сообщениями (сек.)
    --only-waiting  # слать только тем, у кого уже включён флаг ожидания (по умолчанию False)
"""

import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from telegram import Bot

from bot.models import TelegramUser


PROMPT_TEXT = (
    "Сегодня мы предлагаем тебе написать письмо себе в будущее.\n\n"
    "Про этот год. Про то, что было важно, сложно и радостно. Про амбиции, сомнения и то, что для тебя было по-настоящему значимым.\n\n"
    "Напиши его ответным сообщением прямо здесь. Мы сохраним это письмо и отправим его тебе ровно через год. "
    "В день, когда будет особенно ценно оглянуться назад, увидеть пройденный путь и напомнить себе, что всё к лучшему 💛"
)


class Command(BaseCommand):
    help = "Рассылка сообщения с просьбой написать письмо себе в будущее"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delay",
            type=float,
            default=0.05,
            help="Задержка между сообщениями в секундах (по умолчанию 0.05)",
        )
        parser.add_argument(
            "--only-waiting",
            action="store_true",
            help="Отправлять только пользователям, у которых уже is_waiting_future_letter=True",
        )

    def handle(self, *args, **options):
        delay = options["delay"]
        only_waiting = options["only_waiting"]
        token = settings.TELEGRAM_BOT_TOKEN

        if not token:
            self.stderr.write("TELEGRAM_BOT_TOKEN не задан в настройках.")
            return

        qs = TelegramUser.objects.filter(
            telegram_id__isnull=False,
            telegram_id__gt=0,
        )
        if only_waiting:
            qs = qs.filter(is_waiting_future_letter=True)

        users = list(qs)
        total = len(users)
        self.stdout.write(f"Пользователей для рассылки: {total}")

        sent = 0
        errors = 0
        now = timezone.now()

        # Важно: обновляем БД в синхронном контексте (ORM нельзя дергать из async)
        user_ids = [u.id for u in users]
        if user_ids and not only_waiting:
            TelegramUser.objects.filter(id__in=user_ids).update(
                is_waiting_future_letter=True,
                future_letter_requested_at=now,
                updated_at=now,
            )

        async def send_all():
            nonlocal sent, errors
            bot = Bot(token=token)
            for user in users:
                try:
                    # Только отправка — без ORM, чтобы не падать в async-контексте
                    await bot.send_message(
                        chat_id=user.telegram_id,
                        text=PROMPT_TEXT,
                    )
                    sent += 1
                    if delay:
                        await asyncio.sleep(delay)
                except Exception as e:
                    errors += 1
                    self.stderr.write(f"Ошибка для {user.telegram_id}: {e}")

        asyncio.run(send_all())
        self.stdout.write(f"Готово. Отправлено: {sent}, ошибок: {errors}")


