from rest_framework import serializers
from blog.models import Post, Category, Comment
from accounts.models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializador para usuarios"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'bio', 'profile_pic', 'website']

class CategorySerializer(serializers.ModelSerializer):
    """Serializador para categorías"""
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'post_count']
    
    def get_post_count(self, obj):
        return obj.posts.filter(status='published').count()

class CommentSerializer(serializers.ModelSerializer):
    """Serializador para comentarios"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'content', 'created_at']

class PostListSerializer(serializers.ModelSerializer):
    """Serializador para listar posts"""
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'summary', 'featured_image', 
                  'categories', 'status', 'published_at', 'views_count', 'likes_count']

class PostDetailSerializer(serializers.ModelSerializer):
    """Serializador para detalle de post"""
    author = UserSerializer(read_only=True)
    categories = CategorySerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'title', 'slug', 'author', 'content', 'summary', 
                  'featured_image', 'categories', 'status', 'created_at', 
                  'published_at', 'views_count', 'likes_count', 'comments']