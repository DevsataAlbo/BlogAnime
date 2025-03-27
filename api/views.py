from django.shortcuts import get_object_or_404
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime, timedelta

from blog.models import Post, Category, UserActivity
from accounts.models import User
from .serializers import PostListSerializer, PostDetailSerializer, CategorySerializer

@api_view(['GET'])
def post_list_api(request):
    """API para listar posts"""
    posts = Post.objects.filter(status='published').order_by('-published_at')
    
    # Filtrado por categoría
    category_slug = request.GET.get('category')
    if category_slug:
        posts = posts.filter(categories__slug=category_slug)
    
    # Filtrado por autor
    author_username = request.GET.get('author')
    if author_username:
        posts = posts.filter(author__username=author_username)
    
    # Paginación manual
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    start = (page - 1) * page_size
    end = page * page_size
    
    total_posts = posts.count()
    posts = posts[start:end]
    
    serializer = PostListSerializer(posts, many=True)
    
    return Response({
        'results': serializer.data,
        'count': total_posts,
        'pages': (total_posts + page_size - 1) // page_size,
        'current_page': page
    })

@api_view(['GET'])
def post_detail_api(request, post_id):
    """API para detalle de post"""
    post = get_object_or_404(Post, id=post_id)
    serializer = PostDetailSerializer(post)
    return Response(serializer.data)

@api_view(['GET'])
def category_list_api(request):
    """API para listar categorías"""
    categories = Category.objects.all().order_by('name')
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def search_api(request):
    """API para búsqueda"""
    query = request.GET.get('q', '')
    
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(summary__icontains=query) |
            Q(author__username__icontains=query) |
            Q(categories__name__icontains=query),
            status='published'
        ).distinct()
        
        serializer = PostListSerializer(posts, many=True)
        return Response(serializer.data)
    else:
        return Response([])

@api_view(['GET'])
@permission_classes([IsAdminUser])
def metrics_overview(request):
    """API para métricas generales (solo admin)"""
    # Estadísticas básicas
    total_users = User.objects.count()
    total_posts = Post.objects.count()
    published_posts = Post.objects.filter(status='published').count()
    total_views = UserActivity.objects.filter(action_type='view_post').count()
    
    # Obtener stats de los últimos 30 días
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    new_users_30days = User.objects.filter(date_joined__gte=start_date).count()
    new_posts_30days = Post.objects.filter(created_at__gte=start_date).count()
    views_30days = UserActivity.objects.filter(
        action_type='view_post',
        timestamp__gte=start_date
    ).count()
    
    return Response({
        'total_users': total_users,
        'total_posts': total_posts,
        'published_posts': published_posts,
        'total_views': total_views,
        'new_users_30days': new_users_30days,
        'new_posts_30days': new_posts_30days,
        'views_30days': views_30days,
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def posts_by_day(request):
    """API para obtener posts creados por día (solo admin)"""
    # Rango de fechas para filtrar
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    posts_by_day = Post.objects.filter(
        created_at__gte=start_date,
        created_at__lte=end_date
    ).extra({
        'day': "date(created_at)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    return Response(list(posts_by_day))

@api_view(['GET'])
@permission_classes([IsAdminUser])
def views_by_day(request):
    """API para obtener vistas por día (solo admin)"""
    # Rango de fechas para filtrar
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    views_by_day = UserActivity.objects.filter(
        action_type='view_post',
        timestamp__gte=start_date,
        timestamp__lte=end_date
    ).extra({
        'day': "date(timestamp)"
    }).values('day').annotate(count=Count('id')).order_by('day')
    
    return Response(list(views_by_day))