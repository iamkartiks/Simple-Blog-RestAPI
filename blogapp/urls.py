from django.urls import path, include
from .views import UsersAPIView, MyTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import PostListAPIView, PostDetailAPIView, UserPostAPIView, UpvoteAPIView, CommentAPIView


urlpatterns = [
    path('', UsersAPIView.as_view()),
    path('login/', MyTokenObtainPairView.as_view()),
    path('token/refresh/', TokenRefreshView.as_view()),
    path('post/', PostListAPIView.as_view()),
    path('post/<int:pk>/', PostDetailAPIView.as_view()),
    path('post/<int:pk>/upvote/', UpvoteAPIView.as_view()),
    path('post/<int:pk>/comment/', CommentAPIView.as_view()),
    path('post/<username>/', UserPostAPIView.as_view()),
]