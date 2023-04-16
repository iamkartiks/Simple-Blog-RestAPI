from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Post, Like, Comment, Reply


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length = 8, write_only = True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
        return token
    
class PostSerializer(serializers.ModelSerializer):
    # user = serializers.ReadOnlyField(source = 'user.username')
    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'created', 'updated', 'user', 'like_count')

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = ('id', 'user', 'post')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'user', 'post', 'body', 'created')

class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Reply
        fields = ('id', 'user', 'comment', 'body', 'created_at')