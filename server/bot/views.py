from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
import os
import asyncio
from pathlib import Path
from .models import TelegramUser, CalendarSettings, GiftOpening, PromoCodeUsage
from telegram import Bot
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET"])
def check_user(request):
    """Проверить, есть ли пользователь в базе данных"""
    telegram_id = request.GET.get('id')
    
    if not telegram_id:
        return JsonResponse({'error': 'id parameter is required'}, status=400)
    
    try:
        telegram_id_int = int(telegram_id)
        user = TelegramUser.objects.get(telegram_id=telegram_id_int)
        
        logger.info(f"User {telegram_id_int} found in database")
        return JsonResponse({
            'exists': True,
            'user_id': user.id,
            'telegram_id': user.telegram_id,
            'is_from_rf': user.is_from_rf,
            'position': user.position or None,  # Стек пользователя
        })
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Invalid id parameter'}, status=400)
    except TelegramUser.DoesNotExist:
        logger.warning(f"User {telegram_id} not found in database")
        return JsonResponse({
            'exists': False,
            'message': 'User not found'
        })


@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Простая проверка доступности сервера"""
    return JsonResponse({
        'status': 'ok',
        'message': 'Server is running'
    })


def get_current_calendar_day():
    """Получить текущий день календаря (8-19 декабря) из настроек"""
    settings = CalendarSettings.objects.first()
    if settings:
        # Берем день из даты, установленной в админке
        day = settings.current_date.day
        logger.info(f"Using calendar day from settings: {day} (date: {settings.current_date})")
        return day
    else:
        # Если настроек нет, проверяем текущую дату
        today = timezone.now().date()
        if today.month == 12 and 8 <= today.day <= 19:
            logger.warning(f"No calendar settings found, using today's day: {today.day}")
            return today.day
        else:
            # По умолчанию день 8
            logger.warning(f"No calendar settings found and today is not in December 8-19, using default: 8")
            return 8


@csrf_exempt
@require_http_methods(["GET"])
def get_calendar_status(request):
    """Получить статус календаря для пользователя"""
    import logging
    logger = logging.getLogger(__name__)
    
    # ДЕТАЛЬНОЕ ЛОГИРОВАНИЕ для диагностики 400 ошибки
    logger.error(f"=== GET CALENDAR STATUS REQUEST ===")
    logger.error(f"Request path: {request.path}")
    logger.error(f"Request method: {request.method}")
    logger.error(f"Request GET: {dict(request.GET)}")
    logger.error(f"Request META HTTP_HOST: {request.META.get('HTTP_HOST', 'NOT SET')}")
    logger.error(f"Request META SERVER_NAME: {request.META.get('SERVER_NAME', 'NOT SET')}")
    logger.error(f"Request META QUERY_STRING: {request.META.get('QUERY_STRING', 'NOT SET')}")
    logger.error(f"Request META PATH_INFO: {request.META.get('PATH_INFO', 'NOT SET')}")
    logger.error(f"Request META REQUEST_URI: {request.META.get('REQUEST_URI', 'NOT SET')}")
    
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        logger.error(f"telegram_id not provided. GET params: {dict(request.GET)}")
        return JsonResponse({
            'error': 'telegram_id is required',
            'received_params': dict(request.GET),
            'request_path': request.path,
            'request_method': request.method
        }, status=400)
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Получаем текущий день календаря из настроек
    current_day = get_current_calendar_day()
    
    # Получаем открытые подарки пользователя
    opened_gifts = GiftOpening.objects.filter(user=user).values_list('day', flat=True)
    opened_days = list(opened_gifts)
    
    # Формируем статус для каждого дня (8-19 декабря)
    days_status = []
    for day in range(8, 20):
        if day in opened_days:
            # Если подарок открыт - всегда показываем как открытый
            status = "opened"
        elif day < current_day:
            # Прошедшие дни - если не открыт, значит пропущен
            status = "missed"
        elif day == current_day:
            # Текущий день - можно открыть (если еще не открыт)
            status = "available"
        else:
            # Будущие дни - заблокированы
            status = "locked"
        
        days_status.append({
            'day': day,
            'status': status,
            'is_opened': day in opened_days
        })
    
    response_data = {
        'current_day': current_day,
        'days': days_status
    }
    
    logger.info(f"Calendar status for user {user.telegram_id}: current_day={current_day}, opened_days={opened_days}")
    logger.info(f"Days status details: {[(d['day'], d['status'], d['is_opened']) for d in days_status]}")
    
    return JsonResponse(response_data)


@csrf_exempt
@require_http_methods(["POST"])
def open_gift(request):
    """Открыть подарок за определенный день"""
    try:
        data = json.loads(request.body)
        telegram_id_raw = data.get('telegram_id')
        day_raw = data.get('day')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    
    if telegram_id_raw is None or day_raw is None:
        return JsonResponse({'error': 'telegram_id and day are required'}, status=400)

    # Приводим к int, чтобы сравнения не падали
    try:
        telegram_id = int(telegram_id_raw)
        day = int(day_raw)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'telegram_id and day must be integers'}, status=400)
    
    logger.info(f"open_gift called: telegram_id={telegram_id}, day={day}")
    
    # Проверяем, что день в допустимом диапазоне
    if day < 8 or day > 19:
        return JsonResponse({'error': 'Day must be between 8 and 19'}, status=400)
    
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Получаем текущий день календаря из настроек
    current_day = get_current_calendar_day()
    
    # Проверяем доступность дня
    if day > current_day:
        return JsonResponse({'error': 'This day is not available yet'}, status=403)
    
    if day < current_day:
        # Прошедший день - если не открыт, значит пропущен
        if not GiftOpening.objects.filter(user=user, day=day).exists():
            return JsonResponse({'error': 'This day was missed'}, status=403)
    
    # Проверяем, не открыт ли уже подарок
    if GiftOpening.objects.filter(user=user, day=day).exists():
        return JsonResponse({'error': 'Gift already opened'}, status=400)
    
    # Проверяем, что это текущий день (можно открыть только сегодня)
    if day != current_day:
        return JsonResponse({'error': 'Can only open gift for current day'}, status=403)
    
    # Открываем подарок
    GiftOpening.objects.create(user=user, day=day)
    
    logger.info(f"Gift opened for user {user.telegram_id}, day {day}")
    logger.info(f"Checking if message should be sent for day {day}")

    # Отправляем сообщения в Telegram в зависимости от дня
    if day == 8:
        logger.info(f"Day 8 detected, sending message")
        try:
            async def send_day8_message():
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                await bot.send_message(
                    chat_id=user.telegram_id,
                    text=(
                        "Твой первый подарок — пак аватарок на все случаи жизни: "
                        "https://disk.360.yandex.ru/d/M5vqMdNsudNk6Q\n\n"
                        "Возвращайся завтра за следующим призом!"
                    )
                )
            
            asyncio.run(send_day8_message())
            logger.info(f"Day 8 gift message sent to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send day 8 gift message to {user.telegram_id}: {e}", exc_info=True)
    
    elif day == 13:
        logger.info(f"Day 13 detected, sending message to user {user.telegram_id}")
        try:
            async def send_day13_message():
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                message_text = (
                    "Если вы готовитесь к выступлению любого уровня, загляните по ссылке — там собраны полезные слайды, универсальный шаблон для конференций и занятия, которые помогают расти: от базовой подготовки до выходов на международную сцену, работы с питчем и преодоления барьеров\n\n"
                    "Забрать: https://disk.360.yandex.ru/i/OjdruO9xMko_Nw"
                )
                logger.info(f"Attempting to send day 13 message to chat_id: {user.telegram_id}")
                logger.info(f"Bot token present: {bool(settings.TELEGRAM_BOT_TOKEN)}")
                result = await bot.send_message(
                    chat_id=user.telegram_id,
                    text=message_text
                )
                logger.info(f"Day 13 message sent successfully, message_id: {result.message_id}")
                return result
            
            logger.info(f"Running asyncio.run for day 13 message")
            asyncio.run(send_day13_message())
            logger.info(f"Day 13 gift message sent successfully to user {user.telegram_id}")
        except Exception as e:
            logger.error(f"Failed to send day 13 gift message to {user.telegram_id}: {e}", exc_info=True)
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Exception details: {str(e)}")
    
    return JsonResponse({
        'success': True,
        'day': day,
        'opened_at': timezone.now().isoformat()
    })


@csrf_exempt
@require_http_methods(["POST"])
def claim_promo_code(request):
    """Получить промокод для дня 16 декабря"""
    try:
        data = json.loads(request.body)
        telegram_id_raw = data.get('telegram_id')
        day_raw = data.get('day')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    
    if telegram_id_raw is None or day_raw is None:
        return JsonResponse({'error': 'telegram_id and day are required'}, status=400)

    try:
        telegram_id = int(telegram_id_raw)
        day = int(day_raw)
    except (ValueError, TypeError):
        return JsonResponse({'error': 'telegram_id and day must be integers'}, status=400)
    
    # Проверяем, что это день 12
    if day != 16:
        return JsonResponse({'error': 'This endpoint is only for day 16'}, status=400)
    
    try:
        user = TelegramUser.objects.get(telegram_id=telegram_id)
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Проверяем, получал ли пользователь уже промокод для дня 12
    # Проверяем через GiftOpening для дня 12 (единообразно для всех пользователей)
    if GiftOpening.objects.filter(user=user, day=16).exists():
        logger.info(f"User {user.telegram_id} already claimed promo code for day 16")
        return JsonResponse({
            'success': True,
            'already_claimed': True,
            'message': 'Promo code already sent for day 16'
        })
    
    # Загружаем promo-users.json
    # Используем BASE_DIR из settings, который указывает на директорию server/
    promo_users_path = settings.BASE_DIR / 'promo-users.json'
    promo_reserve_path = settings.BASE_DIR / 'promo-reserve.json'
    
    logger.info(f"Looking for promo-users.json at: {promo_users_path}")
    logger.info(f"BASE_DIR: {settings.BASE_DIR}")
    logger.info(f"File exists: {promo_users_path.exists()}")
    
    try:
        with open(promo_users_path, 'r', encoding='utf-8') as f:
            promo_users = json.load(f)
        logger.info(f"Successfully loaded {len(promo_users)} promo users")
    except FileNotFoundError:
        logger.error(f"promo-users.json not found at {promo_users_path}")
        logger.error(f"BASE_DIR: {settings.BASE_DIR}")
        logger.error(f"Absolute path: {promo_users_path.resolve()}")
        return JsonResponse({'error': 'Promo users file not found'}, status=500)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse promo-users.json: {e}")
        return JsonResponse({'error': 'Invalid promo users file'}, status=500)
    
    # Ищем пользователя в promo-users.json по username (nickname)
    user_promo = None
    if user.username:
        # Убираем @ если есть
        username_clean = user.username.lstrip('@')
        for promo_user in promo_users:
            if promo_user.get('nickname', '').lower() == username_clean.lower():
                user_promo = promo_user
                break
    
    # Определяем сообщение и промокод
    message_text = ""
    promocode = ""
    
    if user_promo:
        # Пользователь найден в promo-users.json
        promocode = user_promo.get('promocode', '')
        role = user_promo.get('role', '').lower()
        
        if role == 'афиша':
            message_text = (
                "Твой персональный промокод действует 1 год. Воспользоваться можно только один раз.\n\n"
                f"Промокод: {promocode}"
            )
        elif role == 'маркет':
            message_text = (
                "Твой персональный промокод действует 1 год. Воспользоваться можно только один раз.\n\n"
                f"Промокод: {promocode}"
            )
        else:
            # Если роль не определена, используем сообщение про маркет
            message_text = (
                "Твой персональный промокод действует 1 год. Воспользоваться можно только один раз.\n\n"
                f"Промокод: {promocode}"
            )
    else:
        # Пользователь не найден в promo-users.json - берем из резерва
        try:
            logger.info(f"Looking for promo-reserve.json at: {promo_reserve_path}")
            logger.info(f"File exists: {promo_reserve_path.exists()}")
            with open(promo_reserve_path, 'r', encoding='utf-8') as f:
                promo_reserve = json.load(f)
            logger.info(f"Successfully loaded {len(promo_reserve)} reserve promocodes")
        except FileNotFoundError:
            logger.error(f"promo-reserve.json not found at {promo_reserve_path}")
            logger.error(f"Absolute path: {promo_reserve_path.resolve()}")
            return JsonResponse({'error': 'Promo reserve file not found'}, status=500)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse promo-reserve.json: {e}")
            return JsonResponse({'error': 'Invalid promo reserve file'}, status=500)
        
        # Проверяем, какие промокоды уже использованы
        used_promocodes = set(
            PromoCodeUsage.objects.values_list('promocode', flat=True)
        )
        
        # Находим первый неиспользованный промокод
        available_promocode = None
        for promo in promo_reserve:
            if promo not in used_promocodes:
                available_promocode = promo
                break
        
        if not available_promocode:
            logger.error("No available promocodes in reserve")
            return JsonResponse({'error': 'No available promocodes'}, status=500)
        
        promocode = available_promocode
        
        # Сохраняем использование промокода
        PromoCodeUsage.objects.create(
            promocode=promocode,
            user=user
        )
        
        message_text = (
            "Твой персональный промокод на Яндекс Маркет\n\n"
            "Иногда идеальный подарок — это выбрать что-то для себя. Полезное, уютное или просто приятное.\n\n"
            "Если вы сейчас вне РФ и в течение года у вас не будет возможности воспользоваться промокодом, вы всё равно можете порадовать им близких в России — пусть подарок достанется тем, кому он сейчас будет особенно полезен\n\n"
            f"Промокод: {promocode}"
        )
    
    # Отправляем сообщение в Telegram (асинхронно)
    try:
        async def send_message():
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            result = await bot.send_message(
                chat_id=user.telegram_id,
                text=message_text
            )
            logger.info(f"Message sent successfully to {user.telegram_id}, message_id: {result.message_id}")
            return result
        
        asyncio.run(send_message())
        logger.info(f"Promo code sent to user {user.telegram_id}: {promocode}")
    except Exception as e:
        logger.error(f"Failed to send promo code message to {user.telegram_id}: {e}", exc_info=True)
        # Не возвращаем ошибку, чтобы пользователь все равно получил ответ об успехе
        # Но логируем для диагностики
        logger.warning(f"Promo code was processed but message sending failed: {promocode}")
    
    # Сохраняем запись о получении промокода (для пользователей из promo-users.json тоже)
    # Это предотвратит повторную выдачу
    if not user_promo:
        # Для пользователей из резерва уже создали PromoCodeUsage выше
        pass
    else:
        # Для пользователей из promo-users.json создаем запись в PromoCodeUsage
        # чтобы отслеживать, что они получили промокод
        PromoCodeUsage.objects.get_or_create(
            promocode=promocode,
            user=user,
            defaults={'promocode': promocode, 'user': user}
        )
    
    # Также создаем запись в GiftOpening для дня 12, чтобы это было единообразно
    GiftOpening.objects.get_or_create(
        user=user,
        day=16,
        defaults={'user': user, 'day': 16}
    )
    
    return JsonResponse({
        'success': True,
        'promocode': promocode,
        'sent_at': timezone.now().isoformat()
    })

