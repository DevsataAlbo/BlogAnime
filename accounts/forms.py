from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import User

class CustomUserCreationForm(UserCreationForm):
    """Formulario personalizado de registro de usuario"""
    email = forms.EmailField(
        label=_("Email"),
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full', 
                                       'placeholder': 'usuario@ejemplo.com'})
    )
    
    username = forms.CharField(
        label=_("Nombre de usuario"),
        widget=forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                      'placeholder': 'usuario123'})
    )
    
    password1 = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                          'placeholder': 'Contraseña'})
    )
    
    password2 = forms.CharField(
        label=_("Confirmar contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                          'placeholder': 'Confirmar contraseña'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Formulario personalizado de inicio de sesión"""
    username = forms.CharField(
        label=_("Usuario o Email"),
        widget=forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                      'placeholder': 'usuario o email'})
    )
    
    password = forms.CharField(
        label=_("Contraseña"),
        widget=forms.PasswordInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                          'placeholder': 'Contraseña'})
    )

class UserProfileForm(forms.ModelForm):
    """Formulario para editar perfil de usuario"""
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'bio', 'profile_pic', 
                  'website', 'twitter', 'instagram')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'email': forms.EmailInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full', 'rows': 4}),
            'profile_pic': forms.FileInput(attrs={'class': 'form-input mt-1 block w-full'}),
            'website': forms.URLInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'twitter': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
            'instagram': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full'}),
        }