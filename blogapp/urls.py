from django.urls import path, include
from .views import UsersAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PostListAPIView, PostDetailAPIView, UserPostAPIView, LikeAPIView, CommentAPIView, PostSearchAPIView,ReplyAPIView , AddUserAPI


urlpatterns = [
    path('', UsersAPIView.as_view()),
    path('adduser/', AddUserAPI.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('post/', PostListAPIView.as_view()),
    path('post/<int:pk>/', PostDetailAPIView.as_view()),
    path('post/<int:pk>/upvote/', LikeAPIView.as_view()),
    path('post/<int:pk>/comment/', CommentAPIView.as_view()),
    path('post/<username>/', UserPostAPIView.as_view()),
    path('posts/search/', PostSearchAPIView.as_view()),
    path('comment/<int:pk>/reply/', ReplyAPIView.as_view()),

]