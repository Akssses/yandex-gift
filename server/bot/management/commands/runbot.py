from django.core.management.base import BaseCommand
from telegram import Update
from bot.bot import setup_bot


class Command(BaseCommand):
    help = 'Запускает Telegram бота'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Запуск Telegram бота...'))
        
        application = setup_bot()
        
        # Запускаем бота
        application.run_polling(allowed_updates=Update.ALL_TYPES)
