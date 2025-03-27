from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Post, Category, Comment
from django_summernote.widgets import SummernoteWidget

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title', 'summary', 'content', 'featured_image', 'categories', 'status')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Escribe un título atractivo'}),
            'summary': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Breve descripción del contenido del post'}),
            'content': SummernoteWidget(),
            'featured_image': forms.FileInput(attrs={'class': 'hidden'}),
            'status': forms.Select(attrs={'class': 'form-input custom-select'}),
        }

class CategoryForm(forms.ModelForm):
    """Formulario para crear y editar categorías"""
    class Meta:
        model = Category
        fields = ('name', 'description')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm mt-1 block w-full',
                                           'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full',
                                                 'rows': 3, 'placeholder': 'Descripción breve de la categoría'}),
        }

class CommentForm(forms.ModelForm):
    """Formulario para comentarios en los posts"""
    class Meta:
        model = Comment
        fields = ('content',)
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-textarea rounded-md shadow-sm mt-1 block w-full',
                                             'rows': 3, 'placeholder': 'Escribe tu comentario...'}),
        }

class SearchForm(forms.Form):
    """Formulario de búsqueda"""
    query = forms.CharField(
        label='',
        widget=forms.TextInput(attrs={'class': 'form-input rounded-md shadow-sm block w-full',
                                      'placeholder': 'Buscar posts...'}),
        required=False
    )