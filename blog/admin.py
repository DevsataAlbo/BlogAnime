from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Category, Post, Comment, PostAnalytics, UserActivity


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Admin para las categorías"""
    list_display = ('name', 'slug', 'post_count', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'


class CommentInline(admin.TabularInline):
    """Inline para comentarios en el admin de posts"""
    model = Comment
    extra = 0
    readonly_fields = ('created_at',)


class PostAnalyticsInline(admin.StackedInline):
    """Inline para analíticas en el admin de posts"""
    model = PostAnalytics
    can_delete = False
    readonly_fields = ('views', 'unique_visitors', 'likes', 'shares', 'avg_time_spent')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin para los posts"""
    list_display = ('title', 'author', 'status', 'display_categories', 'published_at', 'views_count', 'comments_count')
    list_filter = ('status', 'created_at', 'published_at', 'categories')
    search_fields = ('title', 'content', 'summary', 'author__username')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'published_at'
    inlines = [PostAnalyticsInline, CommentInline]
    readonly_fields = ('views_count', 'likes_count', 'display_featured_image')
    filter_horizontal = ('categories',)
    
    def display_categories(self, obj):
        """Mostrar categorías como lista"""
        return ", ".join([category.name for category in obj.categories.all()])
    display_categories.short_description = _('Categories')
    
    def comments_count(self, obj):
        """Mostrar número de comentarios"""
        return obj.comments.count()
    comments_count.short_description = _('Comments')
    
    def display_featured_image(self, obj):
        """Mostrar vista previa de la imagen destacada"""
        if obj.featured_image:
            return format_html('<img src="{}" width="300" />', obj.featured_image.url)
        return _('No image')
    display_featured_image.short_description = _('Featured Image Preview')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'status', 'categories')
        }),
        (_('Content'), {
            'fields': ('summary', 'content', 'featured_image', 'display_featured_image')
        }),
        (_('Metrics'), {
            'fields': ('views_count', 'likes_count'),
            'classes': ('collapse',)
        }),
        (_('Dates'), {
            'fields': ('created_at', 'published_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer que created_at y published_at sean solo lectura si el objeto ya existe"""
        if obj:
            return self.readonly_fields + ('created_at',)
        return self.readonly_fields


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin para los comentarios"""
    list_display = ('user', 'post', 'created_at', 'truncated_content')
    list_filter = ('created_at', 'user')
    search_fields = ('content', 'user__username', 'post__title')
    raw_id_fields = ('user', 'post')
    readonly_fields = ('created_at',)
    
    def truncated_content(self, obj):
        """Mostrar contenido truncado"""
        if len(obj.content) > 50:
            return obj.content[:50] + '...'
        return obj.content
    truncated_content.short_description = _('Content')


@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    """Admin para analíticas"""
    list_display = ('post', 'views', 'unique_visitors', 'likes', 'shares', 'avg_time_spent')
    search_fields = ('post__title',)
    list_filter = ('post__status',)
    raw_id_fields = ('post',)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    """Admin para actividad de usuarios"""
    list_display = ('user', 'action_type', 'ip_address', 'timestamp')
    list_filter = ('action_type', 'timestamp')
    search_fields = ('user__username', 'ip_address', 'action_type')
    raw_id_fields = ('user',)
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'