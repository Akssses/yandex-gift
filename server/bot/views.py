from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
import json
from .models import TelegramUser, CalendarSettings, GiftOpening


@csrf_exempt
@require_http_methods(["GET"])
def get_calendar_status(request):
    """Получить статус календаря для пользователя"""
    telegram_id = request.GET.get('telegram_id')
    
    if not telegram_id:
        return JsonResponse({'error': 'telegram_id is required'}, status=400)
    
    try:
        user = TelegramUser.objects.get(telegram_id=int(telegram_id))
    except TelegramUser.DoesNotExist:
        return JsonResponse({'error': 'User not found'}, status=404)
    
    # Получаем текущую дату из настроек
    current_date = CalendarSettings.get_current_date()
    current_day = current_date.day
    
    # Получаем открытые подарки пользователя
    opened_gifts = GiftOpening.objects.filter(user=user).values_list('day', flat=True)
    opened_days = list(opened_gifts)
    
    # Формируем статус для каждого дня (8-19 декабря)
    days_status = []
    for day in range(8, 20):
        if day < current_day:
            # Прошедшие дни - проверяем, открыл ли пользователь
            status = "opened" if day in opened_days else "missed"
        elif day == current_day:
            # Текущий день - можно открыть
            status = "opened" if day in opened_days else "available"
        else:
            # Будущие дни - заблокированы
            status = "locked"
        
        days_status.append({
            'day': day,
            'status': status,
            'is_opened': day in opened_days
        })
    
    return JsonResponse({
        'current_day': current_day,
        'days': days_status
    })


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
    
    # Получаем текущую дату из настроек
    current_date = CalendarSettings.get_current_date()
    current_day = current_date.day
    
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
