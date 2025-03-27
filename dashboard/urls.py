from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.index, name='index'),
    
    # Rutas para gestión de posts
    path('posts/', views.post_list, name='post_list'),
    path('posts/create/', views.post_create, name='post_create'),
    path('posts/edit/<int:post_id>/', views.post_edit, name='post_edit'),
    path('posts/delete/<int:post_id>/', views.post_delete, name='post_delete'),
    
    # Rutas para administradores
    path('all-posts/', views.all_posts_list, name='all_posts_list'),
    path('users/', views.users_list, name='users_list'),
    path('users/edit/<int:user_id>/', views.user_edit, name='user_edit'),
    path('users/delete/<int:user_id>/', views.user_delete, name='user_delete'),
    path('metrics/', views.metrics, name='metrics'),
    
    # Rutas para categorías
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/edit/<int:category_id>/', views.category_edit, name='category_edit'),
    path('categories/delete/<int:category_id>/', views.category_delete, name='category_delete'),
]
