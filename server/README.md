# Django Telegram Bot для адвент-календаря

## Установка

1. Создайте виртуальное окружение:

```bash
python -m venv venv
source venv/bin/activate  # для Linux/Mac
# или
venv\Scripts\activate  # для Windows
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Выполните миграции:

```bash
python manage.py migrate
```

4. Создайте суперпользователя для доступа к админке:

```bash
python manage.py createsuperuser
```

## Запуск

1. Запустите Django сервер (для админки):

```bash
python manage.py runserver
```

2. В другом терминале запустите Telegram бота:

```bash
python manage.py runbot
```

## Использование

### Админка Django

1. Откройте http://127.0.0.1:8000/admin/
2. Войдите с учетными данными суперпользователя
3. В разделе "Пользователи Telegram" создайте нового пользователя:
   - Укажите ник (username)
   - Укажите имя (first_name)
   - Укажите фамилию (last_name)

### Telegram бот

После создания пользователя в админке, он может:

1. Найти бота в Telegram
2. Отправить команду `/start`
3. Пройти диалог:
   - Ввести должность
   - Выбрать территорию (Из РФ / Не из РФ)
   - Открыть мини-аппку (только для пользователей из РФ)

## Настройки

Токен бота и URL мини-аппки настраиваются в `config/settings.py`:

- `TELEGRAM_BOT_TOKEN` - токен Telegram бота
- `MINI_APP_URL` - URL мини-аппки
