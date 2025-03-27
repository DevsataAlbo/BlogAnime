from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('posts/', views.post_list_api, name='post_list_api'),
    path('posts/<int:post_id>/', views.post_detail_api, name='post_detail_api'),
    path('categories/', views.category_list_api, name='category_list_api'),
    path('search/', views.search_api, name='search_api'),
    
    # Endpoints para métricas (admin)
    path('metrics/overview/', views.metrics_overview, name='metrics_overview'),
    path('metrics/posts-by-day/', views.posts_by_day, name='posts_by_day'),
    path('metrics/views-by-day/', views.views_by_day, name='views_by_day'),
]