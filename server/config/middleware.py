"""
Кастомный middleware для отключения CSRF проверки для API endpoints
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings


class DisableCSRFForAPI(MiddlewareMixin):
    """
    Отключает CSRF проверку для API endpoints
    """
    def process_request(self, request):
        # Отключаем CSRF для всех API endpoints
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            # Также убираем Origin из заголовков, чтобы Django не проверял его
            if 'HTTP_ORIGIN' in request.META:
                # Сохраняем для возможного использования
                request._original_origin = request.META.get('HTTP_ORIGIN')
                # Удаляем, чтобы Django не проверял trusted origins
                del request.META['HTTP_ORIGIN']
        return None
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Дополнительно отключаем CSRF для API
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
        return None
