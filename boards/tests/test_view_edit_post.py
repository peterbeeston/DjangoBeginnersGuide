from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from ..models import Board, Post, Topic
from ..views import PostUpdateView

class PostUpdateViewTestCase(TestCase):
    '''
    Base class to be used in all 'PostUpdateView' view tests
    '''
    def setUp(self):
        self.board = Board.objects.create(name='Test Board', description='A test board')
        self.username = 'TestUser'
        self.password = '123'
        user = User.objects.create_user(username=self.username, email='testuser@mail.com', password=self.password)
        self.topic = Topic.objects.create(subject='Test Topic', board=self.board, starter=user)
        self.post = Post.objects.create(message='Test Message', topic=self.topic, created_by=user)
        self.url = reverse(
            'edit_post',
            kwargs={
                'pk': self.board.pk,
                'topic_pk': self.topic.pk,
                'post_pk': self.post.pk
            }
        )

class LoginRequiredPostUpdateViewTests(PostUpdateViewTestCase):
    def test_redirection(self):
        '''
        Test that only logged in users can edit the posts
        '''
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))

class UnauthorisedPostUpdateViewTests(PostUpdateViewTestCase):
    def setUp(self):
        '''
        Create a new user that is different from the one that posted
        '''
        super().setUp()
        username = 'SecondTestUser'
        password = '321'
        user = User.objects.create_user(username=username, email='secondtestuser@mail.com', password=password)
        self.client.login(username=username, password=password)
        self.response = self.client.get(self.url)

    def test_status_code(self):
        '''
        A topic should only be edited by the owner
        Unauthorised users should get a 404 response (Page Not Found)
        '''
        self.assertEqual(self.response.status_code, 404)
