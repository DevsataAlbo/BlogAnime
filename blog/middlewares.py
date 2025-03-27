import re
from django.utils import timezone
from .models import UserActivity, Post
from django.http import Http404, HttpResponseNotFound
from django.template.loader import render_to_string
from django.utils.translation import gettext as _

class UserActivityMiddleware:
    """Middleware para rastrear actividad de usuarios"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Patrones para detectar acciones
        self.post_detail_pattern = re.compile(r'^/post/([a-zA-Z0-9-]+)/$')
        self.category_pattern = re.compile(r'^/category/([a-zA-Z0-9-]+)/$')
        self.search_pattern = re.compile(r'^/search/')
        
    def __call__(self, request):
        # Procesa la solicitud
        response = self.get_response(request)
        
        # Rastrear actividad después de procesar la respuesta
        self.track_activity(request)
        
        return response
    
    def track_activity(self, request):
        """Rastrear actividad del usuario basada en la URL"""
        # No rastrear solicitudes de administración, estáticas o archivos de medios
        if request.path.startswith('/admin/') or request.path.startswith('/static/') or request.path.startswith('/media/'):
            return
        
        # Determinar el tipo de acción
        action_type = self._get_action_type(request)
        if not action_type:
            return
        
        # Obtener la dirección IP y el agente de usuario
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Crear registro de actividad
        UserActivity.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type=action_type,
            ip_address=ip_address,
            user_agent=user_agent,
            timestamp=timezone.now()
        )
    
    def _get_action_type(self, request):
        """Determinar el tipo de acción basada en la URL"""
        path = request.path
        
        # Página principal
        if path == '/':
            return 'view_home'
        
        # Vista de detalle de post
        post_match = self.post_detail_pattern.match(path)
        if post_match:
            slug = post_match.group(1)
            try:
                post = Post.objects.get(slug=slug)
                return f'view_post_{post.id}'
            except Post.DoesNotExist:
                pass
        
        # Vista de categoría
        category_match = self.category_pattern.match(path)
        if category_match:
            return 'view_category'
        
        # Búsqueda
        if self.search_pattern.match(path):
            return 'search'
        
        # Login/Registro
        if path == '/accounts/login/':
            return 'login_attempt'
        
        if path == '/accounts/register/':
            return 'register_attempt'
        
        # Dashboard
        if path.startswith('/dashboard/'):
            return 'dashboard_access'
        
        return None
    
    def _get_client_ip(self, request):
        """Obtener la dirección IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

class Custom404Middleware:
    """Middleware para personalizar las respuestas 404"""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Si la respuesta es un 404, renderizamos nuestra plantilla personalizada
        if response.status_code == 404:
            response = HttpResponseNotFound(
                render_to_string('404.html', request=request)
            )
        
        return response