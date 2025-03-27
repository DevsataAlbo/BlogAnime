# dashboard/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta

from blog.models import Post, Category, Comment, PostAnalytics, UserActivity
from blog.forms import PostForm, CategoryForm
from accounts.models import User
from accounts.forms import UserProfileForm

@login_required
def index(request):
    """Vista principal del dashboard"""
    if request.user.is_admin():
        # Vista para admin
        return admin_dashboard(request)
    else:
        # Vista para autor
        return author_dashboard(request)

@login_required
def author_dashboard(request):
    """Dashboard para autores"""
    # Estadísticas básicas
    total_posts = Post.objects.filter(author=request.user).count()
    published_posts = Post.objects.filter(author=request.user, status='published').count()
    draft_posts = Post.objects.filter(author=request.user, status='draft').count()
    
    # Posts recientes
    recent_posts = Post.objects.filter(author=request.user).order_by('-created_at')[:5]
    
    # Posts más populares
    popular_posts = Post.objects.filter(
        author=request.user, 
        status='published'
    ).order_by('-views_count')[:5]
    
    # Categorías utilizadas
    categories = Category.objects.filter(
        posts__author=request.user
    ).annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:5]
    
    context = {
        'total_posts': total_posts,
        'published_posts': published_posts,
        'draft_posts': draft_posts,
        'recent_posts': recent_posts,
        'popular_posts': popular_posts,
        'categories': categories,
    }
    return render(request, 'dashboard/author/index.html', context)

@staff_member_required
def admin_dashboard(request):
    """Dashboard para administradores"""
    # Estadísticas generales
    total_users = User.objects.count()
    total_authors = User.objects.filter(role__in=['author', 'admin']).count()
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    
    # Posts recientes
    recent_posts = Post.objects.order_by('-created_at')[:8]
    
    # Usuarios recientes
    recent_users = User.objects.order_by('-date_joined')[:8]
    
    # Posts más populares
    popular_posts = Post.objects.filter(
        status='published'
    ).order_by('-views_count')[:8]
    
    # Actividad reciente
    recent_activity = UserActivity.objects.order_by('-timestamp')[:15]
    
    # Estadísticas de contenido
    post_status_count = {
        'published': published_posts,
        'draft': total_posts - published_posts,
    }
    
    # Estadísticas por categoría
    category_stats = Category.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    context = {
        'total_users': total_users,
        'total_authors': total_authors,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'recent_posts': recent_posts,
        'recent_users': recent_users,
        'popular_posts': popular_posts,
        'recent_activity': recent_activity,
        'post_status_count': post_status_count,
        'category_stats': category_stats,
    }
    return render(request, 'dashboard/admin/index.html', context)

@login_required
def post_list(request):
    """Vista para listar posts del autor"""
    posts_list = Post.objects.filter(author=request.user).order_by('-created_at')
    
    # Paginación
    paginator = Paginator(posts_list, 10)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
        
    return render(request, 'dashboard/author/posts.html', {'posts': posts})

@staff_member_required
def all_posts_list(request):
    """Vista para listar todos los posts (admin)"""
    posts_list = Post.objects.all().order_by('-created_at')
    
    # Filtrado por autor
    author_id = request.GET.get('author')
    if author_id:
        posts_list = posts_list.filter(author_id=author_id)
    
    # Filtrado por estado
    status = request.GET.get('status')
    if status:
        posts_list = posts_list.filter(status=status)
    
    # Filtrado por categoría
    category_id = request.GET.get('category')
    if category_id:
        posts_list = posts_list.filter(categories__id=category_id)
    
    # Paginación
    paginator = Paginator(posts_list, 15)
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    # Datos para filtros
    authors = User.objects.filter(role__in=['author', 'admin'])
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'authors': authors,
        'categories': categories,
        'current_author': author_id,
        'current_status': status,
        'current_category': category_id,
    }
    return render(request, 'dashboard/admin/all_posts.html', context)

@login_required
def post_create(request):
    """Vista para crear un nuevo post"""
    if not (request.user.is_author() or request.user.is_admin()):
        messages.error(request, _("No tienes permisos para crear posts."))
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            
            if 'publish' in request.POST:
                post.status = 'published'
                post.published_at = timezone.now()
                action_message = _("¡Post publicado con éxito!")
            else:
                post.status = 'draft'
                action_message = _("¡Post guardado como borrador!")
                
            post.save()
            form.save_m2m()  # Guardar relaciones many-to-many (categorías)
            
            # Crear objeto de analíticas para el post
            PostAnalytics.objects.create(post=post)
            
            messages.success(request, action_message)
            return redirect('dashboard:post_list')
    else:
        form = PostForm()
    
    # Obtener todas las categorías para el selector
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'is_new': True,
        'categories': categories,
    }
    
    return render(request, 'dashboard/author/post_form.html', context)

@login_required
def post_edit(request, post_id):
    """Vista para editar un post"""
    if request.user.is_admin():
        # Admin puede editar cualquier post
        post = get_object_or_404(Post, id=post_id)
    else:
        # Autor solo puede editar sus propios posts
        post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            
            # Determinar acción basada en el botón que se presionó
            if 'publish' in request.POST:
                post.status = 'published'
                if not post.published_at:
                    post.published_at = timezone.now()
                action_message = _("¡Post publicado con éxito!")
            elif 'save_draft' in request.POST:
                post.status = 'draft'
                action_message = _("¡Post guardado como borrador!")
            else:
                action_message = _("¡Post actualizado con éxito!")
                
            post.save()
            form.save_m2m()
            
            messages.success(request, action_message)
            
            if request.user.is_admin() and request.user != post.author:
                return redirect('dashboard:all_posts_list')
            else:
                return redirect('dashboard:post_list')
    else:
        form = PostForm(instance=post)
    
    # Obtener todas las categorías para el selector
    categories = Category.objects.all()
    
    context = {
        'form': form,
        'post': post,
        'is_new': False,
        'categories': categories,
    }
    
    return render(request, 'dashboard/author/post_form.html', context)

@login_required
def post_delete(request, post_id):
    """Vista para eliminar un post"""
    if request.user.is_admin():
        # Admin puede eliminar cualquier post
        post = get_object_or_404(Post, id=post_id)
    else:
        # Autor solo puede eliminar sus propios posts
        post = get_object_or_404(Post, id=post_id, author=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, _("¡Post eliminado con éxito!"))
        
        if request.user.is_admin() and request.user != post.author:
            return redirect('dashboard:all_posts_list')
        else:
            return redirect('dashboard:post_list')
    
    return render(request, 'dashboard/author/post_confirm_delete.html', {'post': post})

@staff_member_required
def users_list(request):
    """Vista para listar usuarios (admin)"""
    users_list = User.objects.all().order_by('-date_joined')
    
    # Filtrado por rol
    role = request.GET.get('role')
    if role:
        users_list = users_list.filter(role=role)
    
    # Paginación
    paginator = Paginator(users_list, 15)
    page = request.GET.get('page')
    try:
        users = paginator.page(page)
    except PageNotAnInteger:
        users = paginator.page(1)
    except EmptyPage:
        users = paginator.page(paginator.num_pages)
    
    context = {
        'users': users,
        'current_role': role,
    }
    return render(request, 'dashboard/admin/users.html', context)

@staff_member_required
def user_edit(request, user_id):
    """Vista para editar usuario (admin)"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _("¡Usuario actualizado con éxito!"))
            return redirect('dashboard:users_list')
    else:
        form = UserProfileForm(instance=user)
    
    return render(request, 'dashboard/admin/user_form.html', {'form': form, 'edit_user': user})

@staff_member_required
def user_delete(request, user_id):
    """Vista para eliminar usuario (admin)"""
    user = get_object_or_404(User, id=user_id)
    
    # No permitir eliminar al propio usuario
    if user == request.user:
        messages.error(request, _("No puedes eliminar tu propio usuario."))
        return redirect('dashboard:users_list')
    
    if request.method == 'POST':
        user.delete()
        messages.success(request, _("¡Usuario eliminado con éxito!"))
        return redirect('dashboard:users_list')
    
    return render(request, 'dashboard/admin/user_confirm_delete.html', {'user': user})

@login_required
def category_list(request):
    """Vista para listar categorías"""
    if request.user.is_admin():
        # Admin ve todas las categorías
        categories = Category.objects.all().order_by('name')
    else:
        # Autor ve solo categorías en sus posts
        categories = Category.objects.filter(
            posts__author=request.user
        ).distinct().order_by('name')
    
    return render(request, 'dashboard/categories.html', {'categories': categories})

@login_required
def category_create(request):
    """Vista para crear categoría"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("¡Categoría creada con éxito!"))
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    
    return render(request, 'dashboard/category_form.html', {'form': form, 'is_new': True})

@login_required
def category_edit(request, category_id):
    """Vista para editar categoría"""
    category = get_object_or_404(Category, id=category_id)
    
    # Verificar permisos (solo admin o autor con posts en esa categoría)
    if not request.user.is_admin():
        has_posts = Post.objects.filter(author=request.user, categories=category).exists()
        if not has_posts:
            messages.error(request, _("No tienes permiso para editar esta categoría."))
            return redirect('dashboard:category_list')
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, _("¡Categoría actualizada con éxito!"))
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    
    return render(request, 'dashboard/category_form.html', {'form': form, 'category': category, 'is_new': False})

@staff_member_required
def category_delete(request, category_id):
    """Vista para eliminar categoría (solo admin)"""
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        category.delete()
        messages.success(request, _("¡Categoría eliminada con éxito!"))
        return redirect('dashboard:category_list')
    
    return render(request, 'dashboard/category_confirm_delete.html', {'category': category})

@staff_member_required
def metrics(request):
    """Vista para mostrar métricas del blog (admin)"""
    # Rango de fechas para filtrar
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Posts por día
    posts_by_day = Post.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).extra({
        'day': "date(created_at)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    # Vistas totales por día
    views_by_day = UserActivity.objects.filter(
        action_type='view_post',
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra({
        'day': "date(timestamp)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    # Usuarios registrados por día
    signups_by_day = User.objects.filter(
        date_joined__gte=start_date,
        date_joined__lte=end_date
    ).extra({
        'day': "date(date_joined)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    # Posts por autor (top 10)
    posts_by_author = User.objects.annotate(
        post_count=Count('posts')
    ).order_by('-post_count')[:10]
    
    # Categorías más populares
    popular_categories = Category.objects.annotate(
        view_count=Count('posts__analytics__views')
    ).order_by('-view_count')[:10]
    
    context = {
        'days': days,
        'posts_by_day': list(posts_by_day),
        'views_by_day': list(views_by_day),
        'signups_by_day': list(signups_by_day),
        'posts_by_author': posts_by_author,
        'popular_categories': popular_categories,
    }
    return render(request, 'dashboard/admin/metrics.html', context)