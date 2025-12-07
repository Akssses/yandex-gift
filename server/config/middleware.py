"""
Кастомный middleware для отключения CSRF проверки для API endpoints
и предотвращения 301 редиректов
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Отключает CSRF проверку для API endpoints и предотвращает редиректы
    """
    def process_request(self, request):
        # Отключаем CSRF для всех API endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            # Предотвращаем редирект для API endpoints
            # Устанавливаем флаг, чтобы CommonMiddleware не делал редирект
            setattr(request, '_should_append_slash', False)
        return None
    
    def process_response(self, request, response):
        # Перехватываем 301 редирект для API endpoints
        if request.path.startswith('/api/') and response.status_code == 301:
            # Если это редирект для API, возвращаем 404 вместо редиректа
            # Это предотвратит потерю тела POST запроса
            from django.http import JsonResponse
            return JsonResponse({
                'error': 'API endpoint not found',
                'path': request.path
            }, status=404)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Дополнительно отключаем CSRF для API
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            setattr(request, '_should_append_slash', False)
        return None
