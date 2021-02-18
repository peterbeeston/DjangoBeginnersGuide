from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm,  SetPasswordForm
from django.contrib.auth.models import User
from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase

class PasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.get(url)
    
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/reset/")
        self.assertEquals(view.func.view_class, auth_views.PasswordResetView)
    
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)
    
    def test_form_inputs(self):
        '''
        The view must contain two inputs: csrf and email
        '''
        self.assertContains(self.response, '<input', 2)         # There should be 2 inputs
        self.assertContains(self.response, 'type="email"', 1)   # The email input

class SuccessfulPasswordResetTests(TestCase):
    def setUp(self):
        email = 'testuser@mail.com'
        User.objects.create(username='Test User', email=email, password='1234abcd')
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': email})
    
    def test_redirection(self):
        '''
        A vaild form submission should redirect the user to the 'password_reset_done' view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)
    
    def test_send_password_reset_email(self):
        self.assertEquals(1, len(mail.outbox))

class InvalidPasswordResetTests(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': 'doesnotexist@mail.com'})
    
    def test_redirection(self):
        '''
        Even invalid emails in the database should redirect the user
        to 'password_reset_done' view
        '''
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)
    
    def test_no_reset_email_sent(self):
        self.assertEquals(0, len(mail.outbox))

class PasswordResetDoneTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)
    
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_view_function(self):
        view = resolve('/reset/done/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetDoneView)

class PasswordResetConfirmTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='TestUser', email='testuser@mail.com', password='1234abcd')
        '''
        Creat a valid password reset token
        based on how django creates the token internally:
        https://https://github.com/django/django/blob/master/django/contrib/auth/forms.py#L304
        '''
        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        url = reverse('password_reset_confirm', kwargs={'uidb64': self.uid, 'token': self.token})
        self.response = self.client.get(url, follow=True)
    
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_view_function(self):
        view = resolve('/reset/{uidb64}/{token}/'.format(uidb64=self.uid, token=self.token))
        self.assertEquals(view.func.view_class, auth_views.PasswordResetConfirmView)
    
    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    
    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)
    
    def test_form_inputs(self):
        '''
        The view must contain three inputs: csrf and two password fields
        '''
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="password"', 2)

class InvalidPasswordresetConfirmationTests(TestCase):
    def setUp(self):
        user = User.objects.create_user(username='TestUser', email='testuser@mail.com', password='1234abcd')
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        '''
        invalidate the token by changing the password
        '''
        user.set_password('abcd1234')
        user.save()

        url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        self.response = self.client.get(url)
    
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_html(self):
        password_reset_url = reverse('password_reset')
        self.assertContains(self.response, 'invalid password reset link')
        self.assertContains(self.response, 'href="{0}"'.format(password_reset_url))

class PasswordResetCompleteTests(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)
    
    def test_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    
    def test_view_function(self):
        view = resolve('/reset/complete/')
        self.assertEquals(view.func.view_class, auth_views.PasswordResetCompleteView)
