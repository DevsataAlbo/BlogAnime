from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm
from .models import User

class RegisterView(SuccessMessageMixin, CreateView):
    """Vista para registro de usuario"""
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('accounts:login')
    success_message = _("¡Tu cuenta ha sido creada con éxito! Ahora puedes iniciar sesión.")

def login_view(request):
    """Vista para inicio de sesión"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                redirect_to = request.GET.get('next', 'dashboard:index')
                return redirect(redirect_to)
        else:
            messages.error(request, _("Usuario o contraseña incorrectos."))
    else:
        form = CustomAuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})

@login_required
def profile(request, username=None):
    """Vista para perfil de usuario"""
    if username:
        # Ver perfil de otro usuario
        user = get_object_or_404(User, username=username)
        posts = user.posts.filter(status='published').order_by('-published_at')
        return render(request, 'accounts/profile.html', {'profile_user': user, 'posts': posts})
    else:
        # Ver propio perfil
        if request.method == 'POST':
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, _("¡Perfil actualizado con éxito!"))
                return redirect('accounts:profile')
        else:
            form = UserProfileForm(instance=request.user)
        
        return render(request, 'accounts/profile_edit.html', {'form': form})