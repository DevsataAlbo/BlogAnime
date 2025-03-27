from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os

def profile_pic_path(instance, filename):
    """Genera la ruta para guardar la foto de perfil"""
    ext = filename.split('.')[-1]
    return os.path.join('profile_pics', f'user_{instance.id}.{ext}')

class User(AbstractUser):
    """Modelo de usuario personalizado"""
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('author', 'Autor'),
        ('reader', 'Lector'),
    )
    
    email = models.EmailField(_('email address'), unique=True)
    bio = models.TextField(_('biography'), blank=True)
    profile_pic = models.ImageField(_('profile picture'), upload_to=profile_pic_path, blank=True, null=True)
    role = models.CharField(_('role'), max_length=10, choices=ROLE_CHOICES, default='reader')
    website = models.URLField(_('website'), blank=True)
    twitter = models.CharField(_('Twitter/X'), max_length=50, blank=True)
    instagram = models.CharField(_('Instagram'), max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
        
    def get_absolute_url(self):
        return reverse('accounts:profile', kwargs={'username': self.username})
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_author(self):
        return self.role == 'author' or self.role == 'admin'