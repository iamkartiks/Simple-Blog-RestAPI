from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions, generics, filters
from .models import Post, Like, Comment
from django.contrib.auth.models import User
from .serializers import PostSerializer, LikeSerializer, CommentSerializer, ReplySerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import MyTokenObtainPairSerializer
from django.db.models import Q


class UsersAPIView(APIView):
    """
    Arguments : API View
    Returns : List of all the users from the database
    
    """
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many = True)
        return Response(serializer.data)


class AddUserAPI(APIView):
    """
    Arguments : API View, request_data
                request_data = ["username","email","password"]
    Returns : created user data (username & email)
    """
    def post(self, request):    
        serializer = UserSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = 201)
        return Response(serializer.errors, status = 400)
    

class MyTokenObtainPairView(TokenObtainPairView):
    """
    Arguments : request_data ["username","password"]
    Returns : tokens (refersh , access) and user_id
    """
    serializer_class = MyTokenObtainPairSerializer


class PostListAPIView(APIView):
    """
    Arguments : request_data ["title", "body"]
    Returns : All Posts before making the POST API call , after that created post
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        data = {
            'user': request.user.id,
            'title': request.data.get('title'),
            'body': request.data.get('body')
        }
        serializer = PostSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)


class PostDetailAPIView(APIView):
    """
        Arguments : request_data ["post_id"]
        Returns : specific post details

        Also allow authenticated user to update, delete their post

    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk = pk)
        except Post.DoesNotExist:
            return None

    def get(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        serializer = PostSerializer(post)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def put(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        data = {
            'user': request.user.id,
            'title': request.data.get('title'),
            'body': request.data.get('body'),
            'like_count': post.like_count
        }
        serializer = PostSerializer(post, data = data, partial = True)
        if serializer.is_valid():
            if post.user.id == request.user.id:
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response({"error": "You are not authorized to edit this post"}, status = status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        if post.user.id == request.user.id:
            post.delete()
            return Response({"res": "Object deleted!"}, status = status.HTTP_200_OK)
        return Response({"error": "You are not authorized to delete this post"}, status = status.HTTP_401_UNAUTHORIZED)


class UserPostAPIView(APIView):
    """
        Arguments : user_name
        Returns : All post made by the specific user

    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, username, *args, **kwargs):
        user = User.objects.filter(username = username).first()
        if user is None:
            return Response({'error': 'User not found'}, status = status.HTTP_404_NOT_FOUND)
        posts = Post.objects.filter(user = user)
        serializer = PostSerializer(posts, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)


class LikeAPIView(APIView):
    """
    Post API for liking the post
    Arguments : 
    Returns : Post detail on which action been taken

    This API call will let user like the post, once they made the POST request it'll upvote the count\
    They can undo it by making another POST request
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk = pk)
        except Post.DoesNotExist:
            return None

    def post(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        
        upvoters = post.likes.all().values_list('user', flat = True)
        if request.user.id in upvoters:
            post.like_count -= 1
            post.likes.filter(user = request.user).delete()
        else:
            post.like_count += 1
            like = Like(user = request.user, post = post)
            like.save()
        post.save()
        serializer = PostSerializer(post)
        return Response(serializer.data, status = status.HTTP_200_OK)


class CommentAPIView(APIView):
    """
    This API will let user add comments on the post

    Arguments : comment body
    Returns : added comment details
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Post.objects.get(pk = pk)
        except Post.DoesNotExist:
            return None
    
    def get(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)
        comments = Comment.objects.filter(post = post)
        serializer = CommentSerializer(comments, many = True)
        return Response(serializer.data, status = status.HTTP_200_OK)

    def post(self, request, pk, *args, **kwargs):
        post = self.get_object(pk)
        if post is None:
            return Response({'error': 'Post not found'}, status = status.HTTP_404_NOT_FOUND)

        data = {
            'user': request.user.id,
            'post': post.id,
            'body': request.data['body'] if isinstance(request.data, dict) else request.data
        }
        serializer = CommentSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    

class PostSearchAPIView(generics.ListAPIView):
    """
    This GET API will let user search specific keywords present in the title or the body of the post

    Arguments : filter keyword <Click on the filter button we'll get on the web page to provide argument>
    Returns : Posts with that keyword otherwise return data with Null values
    
    """
    serializer_class = PostSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'body']

    def get_queryset(self):
        queryset = Post.objects.all()
        query = self.request.query_params.get('query', None)
        if query is not None:
            queryset = queryset.filter(Q(title__icontains=query) | Q(content__icontains=query))
        return queryset


class ReplyAPIView(APIView):
    """
    This API will let people add replies to the specific comments

    Arguments : reply body

    Return : created Reply details
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        try:
            return Comment.objects.get(pk=pk)
        except Comment.DoesNotExist:
            return None

    def post(self, request, pk, *args, **kwargs):
        comment = self.get_object(pk)
        if comment is None:
            return Response({'error': 'Comment not found'}, status=status.HTTP_404_NOT_FOUND)

        data = {
            'user': request.user.id,
            'comment': comment.id,
            'body': request.data['body'] if isinstance(request.data, dict) else request.data
        }
        serializer = ReplySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


