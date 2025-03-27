from .models import Category
from .forms import SearchForm

def categories(request):
    """Contexto para categorías disponibles globalmente"""
    categories_list = Category.objects.all().order_by('name')
    return {
        'global_categories': categories_list,
        'search_form': SearchForm(),
    }

def theme_mode(request):
    """Contexto para el modo claro/oscuro"""
    # Obtener preferencia de tema del usuario desde la cookie
    theme = request.COOKIES.get('theme', 'light')
    return {
        'theme_mode': theme
    }