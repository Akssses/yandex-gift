"""
Отправка писем себе в будущее, срок которых наступил.

Запуск:
    python manage.py send_future_letters

Опции:
    --delay 0.05  # задержка между сообщениями (сек.)
"""

import asyncio

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from telegram import Bot

from bot.models import FutureLetter


def build_delivery_text(letter_text: str) -> str:
    # Можно сделать красивее, но пока минимально и понятно
    return (
        "Твоё письмо себе в будущее 💛\n\n"
        f"{letter_text}"
    )


class Command(BaseCommand):
    help = "Отправляет пользователям письма в будущее, у которых наступила дата отправки"

    def add_arguments(self, parser):
        parser.add_argument(
            "--delay",
            type=float,
            default=0.05,
            help="Задержка между сообщениями в секундах (по умолчанию 0.05)",
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=500,
            help="Сколько писем обработать за запуск (по умолчанию 500)",
        )

    def handle(self, *args, **options):
        delay = options["delay"]
        limit = options["limit"]
        token = settings.TELEGRAM_BOT_TOKEN

        if not token:
            self.stderr.write("TELEGRAM_BOT_TOKEN не задан в настройках.")
            return

        now = timezone.now()

        letters = list(
            FutureLetter.objects.select_related("user")
            .filter(
                Q(sent_at__isnull=True),
                Q(send_at__lte=now),
                Q(user__telegram_id__isnull=False),
                Q(user__telegram_id__gt=0),
            )
            .order_by("send_at")[:limit]
        )

        total = len(letters)
        self.stdout.write(f"Писем к отправке: {total}")

        sent = 0
        errors = 0

        async def send_all():
            nonlocal sent, errors
            bot = Bot(token=token)
            for letter in letters:
                try:
                    await bot.send_message(
                        chat_id=letter.user.telegram_id,
                        text=build_delivery_text(letter.text),
                    )
                    FutureLetter.objects.filter(id=letter.id).update(sent_at=now)
                    sent += 1
                    if delay:
                        await asyncio.sleep(delay)
                except Exception as e:
                    errors += 1
                    self.stderr.write(f"Ошибка для {letter.user.telegram_id} (letter_id={letter.id}): {e}")

        asyncio.run(send_all())
        self.stdout.write(f"Готово. Отправлено: {sent}, ошибок: {errors}")


