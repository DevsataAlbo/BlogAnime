from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, SearchForm
from django.contrib import messages
from django.utils.translation import gettext as _


def index(request):
    """Vista para la página de inicio"""
    featured_posts = Post.objects.filter(status='published').order_by('-published_at')[:5]
    latest_posts = Post.objects.filter(status='published').order_by('-published_at')[5:13]
    popular_posts = Post.objects.filter(status='published').order_by('-views_count')[:5]
    
    # Categorías más populares (con más posts)
    popular_categories = Category.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:8]
    
    context = {
        'featured_posts': featured_posts,
        'latest_posts': latest_posts,
        'popular_posts': popular_posts,
        'popular_categories': popular_categories,
    }
    return render(request, 'blog/index.html', context)

def post_list(request):
    """Vista para listar todos los posts"""
    posts_list = Post.objects.filter(status='published').order_by('-published_at')
    search_form = SearchForm()
    
    # Paginación
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'posts': posts,
        'search_form': search_form,
    }
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    if request.user.is_authenticated and (request.user.is_author() or request.user.is_admin()):
        post = get_object_or_404(Post, slug=slug)
        # Si está en borrador, mostrar un mensaje informativo
        if post.status == 'draft':
            messages.info(request, _("Estás viendo un post en estado de borrador. No está visible para el público."))
    else:
        # Para usuarios normales, solo mostrar posts publicados
        post = get_object_or_404(Post, slug=slug, status='published')
    
    comments = post.comments.all()
    
    # Incrementar contador de vistas (solo si está publicado)
    if post.status == 'published':
        post.views_count += 1
        post.save()
        
        # Si el post tiene analíticas, actualizar
        if hasattr(post, 'analytics'):
            post.analytics.views += 1
            post.analytics.save()
    
    # Posts relacionados (mismas categorías)
    related_posts = Post.objects.filter(
        categories__in=post.categories.all(),
        status='published'
    ).exclude(id=post.id).distinct()[:3]
    
    # Formulario de comentarios
    comment_form = CommentForm()
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'comment_form': comment_form,
        'is_draft': post.status == 'draft',
    }
    return render(request, 'blog/post_detail.html', context)

def category_list(request, slug):
    """Vista para listar posts por categoría"""
    category = get_object_or_404(Category, slug=slug)
    posts_list = Post.objects.filter(
        categories=category,
        status='published'
    ).order_by('-published_at')
    
    # Paginación
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'category': category,
        'posts': posts,
    }
    return render(request, 'blog/category_list.html', context)

def search_results(request):
    """Vista para resultados de búsqueda"""
    form = SearchForm(request.GET)
    posts = []
    
    if form.is_valid():
        query = form.cleaned_data['query']
        if query:
            posts = Post.objects.filter(
                Q(title__icontains=query) | 
                Q(content__icontains=query) |
                Q(summary__icontains=query) |
                Q(author__username__icontains=query) |
                Q(categories__name__icontains=query),
                status='published'
            ).distinct()
    
    context = {
        'posts': posts,
        'search_form': form,
    }
    return render(request, 'blog/search_results.html', context)

@login_required
@require_POST
def add_comment(request, post_id):
    """Vista para agregar comentarios"""
    post = get_object_or_404(Post, id=post_id, status='published')
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.user = request.user
        comment.save()
        
        return redirect('blog:post_detail', slug=post.slug)
    
    # Si hay errores, redirigir al detalle del post con el formulario con errores
    return redirect('blog:post_detail', slug=post.slug)

@login_required
@require_POST
def like_post(request, post_id):
    """Vista para dar like a un post (Ajax)"""
    post = get_object_or_404(Post, id=post_id)
    
    # Incrementar contador de likes
    post.likes_count += 1
    post.save()
    
    # Si el post tiene analíticas, actualizar
    if hasattr(post, 'analytics'):
        post.analytics.likes += 1
        post.analytics.save()
    
    return JsonResponse({'likes': post.likes_count})