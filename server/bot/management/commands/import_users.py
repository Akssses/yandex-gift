"""
Django management команда для импорта пользователей из users.json
"""
import json
import os
from django.core.management.base import BaseCommand
from bot.models import TelegramUser


class Command(BaseCommand):
    help = 'Импортирует пользователей из users.json в базу данных'

    def handle(self, *args, **options):
        # Путь к файлу users.json
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        json_file = os.path.join(base_dir, 'users.json')
        
        if not os.path.exists(json_file):
            self.stdout.write(self.style.ERROR(f'Файл {json_file} не найден!'))
            return
        
        # Читаем JSON файл
        with open(json_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        self.stdout.write(f'Найдено пользователей в файле: {len(users_data)}')
        
        created_count = 0
        updated_count = 0
        skipped_count = 0
        
        for user_data in users_data:
            fullname = user_data.get('fullname', '').strip()
            nickname = user_data.get('nickname')
            
            if not fullname:
                self.stdout.write(self.style.WARNING(f'Пропущен пользователь без имени: {user_data}'))
                skipped_count += 1
                continue
            
            # Разделяем полное имя на имя и фамилию
            name_parts = fullname.split(maxsplit=1)
            if len(name_parts) == 1:
                first_name = name_parts[0]
                last_name = ''
            else:
                first_name = name_parts[0]
                last_name = name_parts[1]
            
            # Проверяем, существует ли пользователь с таким именем и фамилией
            user, created = TelegramUser.objects.get_or_create(
                first_name=first_name,
                last_name=last_name,
                defaults={
                    'username': nickname if nickname else None,
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Создан: {first_name} {last_name} (@{nickname if nickname else "без username"})'))
            else:
                # Обновляем username, если он изменился
                if nickname and user.username != nickname:
                    user.username = nickname
                    user.save()
                    updated_count += 1
                    self.stdout.write(self.style.WARNING(f'↻ Обновлен: {first_name} {last_name} (@{nickname})'))
                else:
                    skipped_count += 1
                    self.stdout.write(f'⊘ Пропущен (уже существует): {first_name} {last_name}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS(f'Импорт завершен:'))
        self.stdout.write(self.style.SUCCESS(f'  Создано: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Обновлено: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'  Пропущено: {skipped_count}'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
