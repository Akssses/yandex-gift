from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
import logging
from .models import TelegramUser, CalendarSettings, GiftOpening

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
    
    # Логируем все GET параметры для отладки
    logger.info(f"GET parameters: {dict(request.GET)}")
    logger.info(f"Request path: {request.path}")
    logger.info(f"Request META: {dict(request.META.get('QUERY_STRING', ''))}")
    
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        logger.warning(f"telegram_id not provided. GET params: {dict(request.GET)}")
        return JsonResponse({
            'error': 'telegram_id is required',
            'received_params': dict(request.GET)
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
        telegram_id = data.get('telegram_id')
        day = data.get('day')
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({'error': 'Invalid request data'}, status=400)
    
    if not telegram_id or not day:
        return JsonResponse({'error': 'telegram_id and day are required'}, status=400)
    
    # Проверяем, что день в допустимом диапазоне
    if day < 8 or day > 19:
        return JsonResponse({'error': 'Day must be between 8 and 19'}, status=400)
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
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
    
    return JsonResponse({
        'success': True,
        'day': day,
        'opened_at': timezone.now().isoformat()
    })

