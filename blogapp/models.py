from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Post(models.Model):
    """
    Post Model which will create instance of Post in database
    """
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    title = models.CharField(max_length = 100)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add = True)
    updated = models.DateTimeField(auto_now = True)
    like_count = models.IntegerField(default = 0)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('post-detail', kwargs = {'pk': self.pk})


class Like(models.Model):
    """
    Like Model which will store like count of the Post data as an separate instance
    """
    user = models.ForeignKey(User, related_name = 'likes', on_delete = models.CASCADE)
    post = models.ForeignKey(Post, related_name = 'likes', on_delete = models.CASCADE)


class Comment(models.Model):
    """
    Comment Model which will store like count of the Post data as an separate instance
    """
    user = models.ForeignKey(User, related_name = 'comments', on_delete = models.CASCADE)
    post = models.ForeignKey(Post, related_name = 'comments', on_delete = models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return self.body

class Reply(models.Model):
    """
    Reply Model which will store like replies of a specific Comment data as an separate instance
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='replies')
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return  self.body