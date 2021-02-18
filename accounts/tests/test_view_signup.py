from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from ..views import signup
from ..forms import SignUpForm

class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve('/signup/')
        self.assertEqual(view.func, signup)

    def test_signup_contains_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')
    
    def test_signuo_contains_usercreationform(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SignUpForm)
    
    def test_form_inputs(self):
        '''
        The view must contain five inputs:
            csrf, username, email, password1, password2
        '''
        self.assertContains(self.response, '<input', 5)             # Five inputs
        self.assertContains(self.response, 'type="text"', 1)        # The username
        self.assertContains(self.response, 'type="email"', 1)       # The email address
        self.assertContains(self.response, 'type="password"', 2)    # The two password fields

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'newUser',
            'email': 'newUser@mail.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.existing_user_count = User.objects.count();
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
    
    def test_redirection(self):
        '''
        A valid form submission should redirect the user to the home page
        '''
        self.assertRedirects(self.response, self.home_url)
    
    def test_user_creation(self):
        self.assertEquals(self.existing_user_count + 1, User.objects.count())
        #self.assertTrue(User.objects.exists())
    
    def test_user_authentication(self):
        '''
        Create a new request to an arbitary page
        The resulting response should now have a 'user' in its context,
        after a successful sign in.
        '''
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)

class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.existing_user_count = User.objects.count();
        self.response = self.client.post(url, {})   # submit an empty dictionary
    
    def test_signup_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEquals(self.response.status_code, 200)
    
    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)
    
    def test_user_not_created(self):
        #self.assertFalse(User.objects.exists())
        self.assertEquals(self.existing_user_count, User.objects.count())