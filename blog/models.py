from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify
from accounts.models import User
import os

class Category(models.Model):
    """Modelo para categorías de posts"""
    name = models.CharField(_('name'), max_length=100, unique=True)
    slug = models.SlugField(_('slug'), max_length=100, unique=True)
    description = models.TextField(_('description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
        ordering = ['name']
        
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('blog:category_list', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def post_count(self):
        return self.posts.filter(status='published').count()

def post_image_path(instance, filename):
    """
    Genera la ruta para guardar las imágenes de los posts.
    Asegura que los nombres de archivo sean seguros, cortos y únicos.
    """
    import os
    import uuid
    from django.utils.text import slugify
    
    try:
        # Obtener la extensión del archivo de forma segura
        ext = filename.split('.')[-1].lower() if '.' in filename else 'jpg'
        
        # Limitar las extensiones a tipos seguros
        if ext not in ['jpg', 'jpeg', 'png', 'gif', 'webp']:
            ext = 'jpg'
        
        # Generar un slug corto basado en el título
        title = instance.title if hasattr(instance, 'title') and instance.title else 'post'
        slug_base = slugify(title)[:15]  # Reducido a 15 caracteres máximo
        
        # Generar un identificador único
        unique_id = str(uuid.uuid4())[:6]  # Reducido a 6 caracteres
        
        # Crear un nombre de archivo limpio y corto
        safe_filename = f"{slug_base}-{unique_id}.{ext}"
        
        # Devolver la ruta completa
        return os.path.join('post_images', safe_filename)
    except Exception as e:
        # En caso de cualquier error, generar un nombre genérico pero válido
        unique_id = str(uuid.uuid4())[:10]
        return os.path.join('post_images', f"post-{unique_id}.jpg")

class Post(models.Model):
    """Modelo para posts del blog"""
    STATUS_CHOICES = (
        ('draft', 'Borrador'),
        ('published', 'Publicado'),
    )
    
    title = models.CharField(_('title'), max_length=255)
    slug = models.SlugField(_('slug'), max_length=255, unique=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField(_('content'))
    summary = models.TextField(_('summary'), max_length=500)
    featured_image = models.ImageField(_('featured image'), upload_to=post_image_path, max_length=500)
    categories = models.ManyToManyField(Category, related_name='posts')
    status = models.CharField(_('status'), max_length=10, choices=STATUS_CHOICES, default='draft')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(blank=True, null=True)
    
    views_count = models.PositiveIntegerField(_('views count'), default=0)
    likes_count = models.PositiveIntegerField(_('likes count'), default=0)
    
    class Meta:
        verbose_name = _('post')
        verbose_name_plural = _('posts')
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_featured_image_url(self):
        """
        Obtiene la URL completa de la imagen destacada.
        Maneja correctamente tanto el entorno de desarrollo como producción con S3.
        """
        if not self.featured_image:
            return None
            
        try:
            # Simplemente devolver la URL generada por Django
            return self.featured_image.url
        except Exception as e:
            # En caso de error, mostrar una URL de imagen por defecto
            return None
        
class Comment(models.Model):
    """Modelo para comentarios en los posts"""
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('comment')
        verbose_name_plural = _('comments')
        ordering = ['-created_at']
        
    def __str__(self):
        return f'Comment by {self.user.username} on {self.post.title}'

class PostAnalytics(models.Model):
    """Modelo para almacenar analíticas de los posts"""
    post = models.OneToOneField(Post, on_delete=models.CASCADE, related_name='analytics')
    views = models.PositiveIntegerField(default=0)
    unique_visitors = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    shares = models.PositiveIntegerField(default=0)
    avg_time_spent = models.FloatField(default=0)  # en segundos
    
    class Meta:
        verbose_name = _('post analytics')
        verbose_name_plural = _('post analytics')
        
    def __str__(self):
        return f'Analytics for {self.post.title}'

class UserActivity(models.Model):
    """Modelo para trackear actividad de usuarios para métricas"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities', null=True, blank=True)
    action_type = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-timestamp']