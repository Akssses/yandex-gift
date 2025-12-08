"""
Кастомный middleware для отключения CSRF проверки для API endpoints
и предотвращения 301 редиректов
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import JsonResponse


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Отключает CSRF проверку для API endpoints и предотвращает редиректы
    """
    def process_request(self, request):
        # Отключаем CSRF для всех API endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            # КРИТИЧНО: отключаем APPEND_SLASH для API endpoints
            # Это предотвратит редирект от CommonMiddleware
            setattr(request, '_should_append_slash', False)
        return None
    
    def process_response(self, request, response):
        # Перехватываем ВСЕ 301 редиректы для API endpoints
        if request.path.startswith('/api/') and response.status_code == 301:
            # Логируем для отладки
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"301 redirect intercepted for API: {request.path} -> {response.get('Location', 'unknown')}"
            )
            # Возвращаем 404 вместо редиректа, чтобы не терять тело POST запроса
            return JsonResponse({
                'error': 'API endpoint not found',
                'path': request.path,
                'message': '301 redirect was intercepted - endpoint may not exist'
            }, status=404)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Дополнительно отключаем CSRF для API
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            setattr(request, '_should_append_slash', False)
        return None
