from django.test import TestCase
from .models import *
from django.test import TestCase
from .forms import UserRegisterForm, SiteForm


class UserRegisterFormTest(TestCase):
    def test_valid_phone_number(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testuser@ukr.net.com',
            'phone': '+380123456789'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_phone_number(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testuser@example.com',
            'phone': '123456789'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)

    def test_passwords_match(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword',
            'password2': 'testpassword',
            'email': 'testuser@example.com',
            'phone': '+380123456789'
        }
        form = UserRegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_passwords_do_not_match(self):
        form_data = {
            'username': 'testuser',
            'password1': 'testpassword1',
            'password2': 'testpassword2',  # Different password
            'email': 'testuser@example.com',
            'phone': '+380123456789'
        }
        form = UserRegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_email_field_exists(self):
        form = UserRegisterForm()
        self.assertTrue('email' in form.fields)

    def test_remember_me_field_not_in_login_form(self):
        form = UserRegisterForm()
        self.assertFalse('remember_me' in form.fields)


class SiteModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.site = Site.objects.create(
            name='Test Site',
            url='http://example.com',
            protocol_security=True,
            user=self.user
        )

    def test_site_str_method(self):
        self.assertEqual(str(self.site), 'Test Site')

    def test_site_model_fields(self):
        self.assertEqual(self.site.name, 'Test Site')
        self.assertEqual(self.site.url, 'http://example.com')
        self.assertTrue(self.site.protocol_security)
        self.assertEqual(self.site.user, self.user)


class SiteFormTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword'
        )
        self.client.force_login(self.user)

    def test_valid_site_form(self):
        form_data = {
            'name': 'Test Site',
            'url': 'http://example.com',
            'protocol_security': True,
        }
        form = SiteForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_invalid_site_form(self):
        # Missing required fields in the form data
        form_data = {}
        form = SiteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        self.assertIn('url', form.errors)
