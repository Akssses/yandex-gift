"""
Кастомный middleware для отключения CSRF проверки для API endpoints
"""
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


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
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        # Дополнительно отключаем CSRF для API
        if request.path.startswith('/api/'):
            setattr(request, '_dont_enforce_csrf_checks', True)
            setattr(request, '_should_append_slash', False)
        return None
