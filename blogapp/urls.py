from django.urls import path, include
from .views import UsersAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PostListAPIView, PostDetailAPIView, UserPostAPIView, LikeAPIView, CommentAPIView, PostSearchAPIView,ReplyAPIView , AddUserAPI


urlpatterns = [
    path('', UsersAPIView.as_view(), name='users-list'),
    path('adduser/', AddUserAPI.as_view(), name='add_user'),
    path('login/', MyTokenObtainPairView.as_view(), name="get-token"),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('post/', PostListAPIView.as_view(), name='post-list'),
    path('post/<int:pk>/', PostDetailAPIView.as_view(), name = 'post-detail'),
    path('post/<int:pk>/upvote/', LikeAPIView.as_view(), name='like'),
    path('post/<int:pk>/comment/', CommentAPIView.as_view(), name='comment'),
    path('post/<username>/', UserPostAPIView.as_view(), name="user-post"),
    path('posts/search/', PostSearchAPIView.as_view(), name='post-search'),
    path('comment/<int:pk>/reply/', ReplyAPIView.as_view(), name="reply-comment"),

]