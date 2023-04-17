from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from .models import Post, Like, Comment, Reply
from .serializers import PostSerializer, CommentSerializer, ReplySerializer

class AuthTestCase(TestCase):
    """
    test for user authentication
    """
    def setUp(self):
        self.u = User.objects.create_user('test@dom.com', 'test@dom.com', 'pass')
        self.u.is_staff = True
        self.u.is_superuser = True
        self.u.is_active = True
        self.u.save()

    def testLogin(self):
        self.client.login(username='test@dom.com', password='pass')

class PostListAPIViewTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client.force_authenticate(user=self.user)

    def test_create_post(self):
        url = reverse('post-list')
        data = {'title': 'Test Post', 'body': 'This is a test post.'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(Post.objects.get().title, 'Test Post')
        self.assertEqual(Post.objects.get().body, 'This is a test post.')
    
    def test_get_all_posts(self):
        url = reverse('post-list')
        response = self.client.get(url)
        posts = Post.objects.all()
        serializer = PostSerializer(posts, many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)



class PostDetailAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username = 'testusername',
            email='testuser@test.com',
            password='testpass',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        self.post = Post.objects.create(
            user=self.user,
            title='Test Title',
            body='Test Body'
        )

    def test_get_post_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Title')
        self.assertEqual(response.data['body'], 'Test Body')
        
    def test_put_post_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        data = {'title': 'New Title', 'body': 'New Body'}
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'New Title')
        self.assertEqual(response.data['body'], 'New Body')
        
    def test_delete_post_detail(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('post-detail', kwargs={'pk': self.post.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['res'], 'Object deleted!')



class UserPostAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(user=self.user, title='Test Post', body='Test Body')

    def test_get_posts_by_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-post', kwargs={'username': self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = PostSerializer([self.post], many=True)
        self.assertEqual(response.data, serializer.data)

    def test_get_posts_by_invalid_user(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('user-post', kwargs={'username': 'invalidusername'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'error': 'User not found'})


class LikeAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'testuser@example.com', 'testpass')
        self.post = Post.objects.create(user=self.user, title='Test post', body='Test body')

    def test_like_post(self):
        url = reverse('like', kwargs={'pk': self.post.pk})
        self.client.force_authenticate(user=self.user)

        # First, like the post
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 1)
        self.assertTrue(Like.objects.filter(user=self.user, post=self.post).exists())

        # Now, undo the like
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['like_count'], 0)
        self.assertFalse(Like.objects.filter(user=self.user, post=self.post).exists())

    def test_like_nonexistent_post(self):
        url = reverse('like', kwargs={'pk': 999})
        self.client.force_authenticate(user=self.user)

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_like_unauthenticated(self):
        url = reverse('like', kwargs={'pk': self.post.pk})

        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




class CommentAPIViewTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.post = Post.objects.create(user=self.user, title='Test Post', body='Test body')
        self.valid_payload = {
            'body': 'Test comment'
        }
        self.invalid_payload = {
            'body': ''
        }
        self.url = reverse('comment', args=[self.post.id])

    def test_get_comments(self):
        response = self.client.get(self.url)
        comments = Comment.objects.filter(post=self.post)
        serializer = CommentSerializer(comments, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_valid_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['body'], self.valid_payload['body'])
        self.assertEqual(response.data['user'], self.user.id)
        self.assertEqual(response.data['post'], self.post.id)

    def test_create_invalid_comment(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, data=self.invalid_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Comment.objects.filter(post=self.post).count(), 0)



class PostSearchAPIViewTestCase(APITestCase):
    def setUp(self):
        # Create some sample posts for testing
        self.post1 = Post.objects.create(title='Test Post 1', body='This is a test post')
        self.post2 = Post.objects.create(title='Test Post 2', body='Another test post')
        self.post3 = Post.objects.create(title='Something else', body='This post has a different title')

    def test_search_posts(self):
        # Search for posts with the keyword "test"
        url = reverse('post-search') + '?query=test'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that the correct posts were returned
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], 'Test Post 1')
        self.assertEqual(response.data[1]['title'], 'Test Post 2')

    def test_search_no_results(self):
        # Search for posts with a keyword that doesn't exist
        url = reverse('post-search') + '?query=foobar'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Check that no posts were returned
        self.assertEqual(len(response.data), 0)

class ReplyAPIViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.comment = Comment.objects.create(user=self.user, post_id=1, body='Test Comment')

    def test_create_reply(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('reply-comment', kwargs={'pk': self.comment.id})
        data = {'body': 'Test Reply'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        reply = Reply.objects.last()
        serializer = ReplySerializer(reply)
        self.assertEqual(response.data, serializer.data)

    def test_create_reply_with_invalid_data(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('reply-comment', kwargs={'pk': self.comment.id})
        data = {'invalid': 'data'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
