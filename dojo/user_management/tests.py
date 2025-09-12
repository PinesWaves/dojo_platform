from datetime import timedelta
from email.mime.image import MIMEImage

from django.test import TestCase, Client
from django.urls import reverse_lazy, reverse
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from unittest.mock import patch, MagicMock

from django.utils import timezone

from .models import Token, TokenType, Category


class CustomLoginViewTest(TestCase):
    """
    To test the login view. Cover both GET and POST requests, and different user scenarios like successful login,
    invalid credentials, and inactive users.
    """
    def setUp(self):
        """
        This method runs before each test method. It's used to create the necessary objects for the tests, such as
        users and the test client.
        """
        self.client = Client()
        self.login_url = reverse_lazy('login')
        self.student_dashboard_url = reverse_lazy('student_dashboard')
        self.sensei_dashboard_url = reverse_lazy('sensei_dashboard')

        self.user_student = get_user_model().objects.create_user(
            email='student@test.com',
            password='testpassword',
            id_number='100',
            category=Category.STUDENT
        )
        self.user_sempai = get_user_model().objects.create_user(
            email='sempai@test.com',
            password='testpassword',
            id_number='200',
            category=Category.SEMPAI
        )
        self.user_sensei = get_user_model().objects.create_user(
            email='sensei@test.com',
            password='testpassword',
            id_number='300',
            category=Category.SENSEI
        )
        self.user_inactive = get_user_model().objects.create_user(
            email='inactive@test.com',
            password='testpassword',
            id_number='400',
            is_active=False
        )

    def test_login_page_get(self):
        """
        Checks that a GET request to the login URL returns a 200 OK status and uses the correct template.
        """
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_register/login.html')


    """
    test_authenticated_user_redirects_* simulates a logged-in user trying to access the login page and asserts
    that they are redirected to their respective dashboard.
    """
    def test_authenticated_user_redirects_student(self):
        self.client.force_login(self.user_student)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.student_dashboard_url)

    def test_authenticated_user_redirects_sempai(self):
        self.client.force_login(self.user_sempai)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.sensei_dashboard_url)

    def test_authenticated_user_redirects_sensei(self):
        self.client.force_login(self.user_sensei)
        response = self.client.get(self.login_url)
        self.assertRedirects(response, self.sensei_dashboard_url)

    """
    test_successful_login_redirects_* Simulates a POST request with correct credentials and asserts that the user is
    redirected and authenticated.
    """
    def test_successful_login_redirects_student(self):
        response = self.client.post(self.login_url, {'id_number': '100', 'password': 'testpassword'})
        self.assertRedirects(response, self.student_dashboard_url)
        self.assertTrue(self.user_student.is_authenticated)

    def test_successful_login_redirects_sempai(self):
        response = self.client.post(self.login_url, {'id_number': '200', 'password': 'testpassword'}, follow=True)
        self.assertRedirects(response, self.sensei_dashboard_url)
        self.assertTrue(self.user_sempai.is_authenticated)

    def test_successful_login_redirects_sensei(self):
        response = self.client.post(self.login_url, {'id_number': '300', 'password': 'testpassword'})
        self.assertRedirects(response, self.sensei_dashboard_url)
        self.assertTrue(self.user_sensei.is_authenticated)

    def test_invalid_credentials(self):
        """
        Tests the case where the user provides incorrect login information. You can use get_messages to check if the
        correct error message is displayed.
        """
        response = self.client.post(self.login_url, {'id_number': 'wrong_id', 'password': 'wrong_password'})
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Invalid credentials.", str(messages[0]))

    def test_inactive_user(self):
        """
        Tests the logic for a user whose account is not active.
        """
        response = self.client.post(self.login_url, {'id_number': '54321', 'password': 'testpassword'})
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Invalid credentials.", str(messages[0]))

    def test_next_url_redirection(self):
        """
        Checks that if a next parameter is provided and is a safe URL, the user is redirected to that URL after a
        successful login.
        """
        next_url = reverse('profile')
        response = self.client.post(
            self.login_url,
            {'id_number': '100', 'password': 'testpassword', 'next': next_url}
        )
        self.assertRedirects(response, next_url)

    def test_unsafe_next_url_redirection(self):
        """
        Ensures that if the next parameter is not a safe URL, the user is redirected to their default dashboard
        instead of the unsafe URL.
        """
        unsafe_next_url = 'http://malicious-site.com'
        response = self.client.post(
            self.login_url,
            {'id_number': '100', 'password': 'testpassword', 'next': unsafe_next_url}
        )
        self.assertRedirects(response, self.student_dashboard_url)


class RegisterViewTest(TestCase):
    """
    Testing the registration view involves checking token validation, valid form submissions, and invalid form
    submissions.
    """
    def setUp(self):
        self.client = Client()
        self.register_url_with_token = reverse('signup', kwargs={'token': 'test_token'})
        self.login_url = reverse_lazy('login')
        self.token = Token.objects.create(
            token='test_token',
            type=TokenType.SIGNUP,
            expires_at=timezone.now() + timedelta(hours=2)
        )

    def test_register_with_valid_token(self):
        """
        Checks that the page loads correctly when a valid token is provided.
        """
        response = self.client.get(self.register_url_with_token)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_register/register.html')
        self.assertIn('token', response.context)

    def test_register_with_invalid_token(self):
        """
        Asserts that an invalid token redirects the user to the login page and sets an error message in the session.
        """
        response = self.client.get(reverse('signup', kwargs={'token': 'invalid_token'}))
        self.assertRedirects(response, self.login_url)
        self.assertEqual(self.client.session.get('errors'), 'Invalid or expired token')

    def test_register_form_valid(self):
        """
        Simulates a successful form submission, checking for redirection, the success message, and verifying that a new
        user object was created in the database.
        """
        form_data = {
            'first_name': 'john',
            'last_name': 'doe',
            'id_type': 'CC',
            'id_number': '22222',
            'gender': 'M',
            'birth_date': '01/01/2000',
            'birth_place': 'bogota',
            'profession': 'lawyer',
            'email': 'newuser@example.com',
            'phone_number': '300 555 5555',
            'country': 'CO',
            'city': 'Bogota',
            'address': 'ABC street',
            'date_joined': '09/09/2025',
            'eps': 'salud total',
            'physical_cond': 'A',
            'medical_cond': 'NA',
            'sec_recom': 'on',
            'agreement': 'on',
            'accept_inf_cons': 'on',
            'accept_regulations': 'on',
            'password1': 'newpassword',
            'password2': 'newpassword',
        }
        response = self.client.post(self.register_url_with_token, form_data, follow=True)
        self.assertRedirects(response, self.login_url)
        self.assertEqual(self.client.session.get('msg'), "Registration successful!")
        self.assertTrue(get_user_model().objects.filter(id_number='22222').exists())

    def test_register_form_invalid(self):
        """
        Simulates an invalid form submission (e.g., mismatched passwords), ensuring that the page re-renders with the
        form and the correct error message.
        """
        form_data = {
            'email': 'newuser@example.com',
            'id_number': '22222',
            'password1': 'newpassword',
            'password2': 'mismatched_password'
        }
        response = self.client.post(self.register_url_with_token, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertFalse(response.context['form'].is_valid())
        self.assertEqual(self.client.session.get('msg'), "Update failed!")


class ForgotPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.forgot_pass_url = reverse_lazy('forgot-password')
        self.user = get_user_model().objects.create_user(
            email='user@test.com',
            password='testpassword',
            id_number='123'
        )

    @patch('email.mime.image.MIMEImage')  # patch where it is defined
    @patch('user_management.views.EmailMultiAlternatives.send')
    def test_forgot_password_sends_email_with_valid_email(self, mock_send_email, mock_mime_image):
        # Make MIMEImage return a real object
        mock_mime_image.side_effect = lambda data: MIMEImage(b'testbytes', _subtype="png")

        form_data = {'email': 'user@test.com'}
        response = self.client.post(self.forgot_pass_url, form_data, follow=True)

        self.assertRedirects(response, reverse_lazy('login'))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("We have sent a password reset link to your email.", str(messages[0]))

        mock_send_email.assert_called_once()
        mock_mime_image.assert_called_once()

    def test_forgot_password_with_non_existent_email(self):
        form_data = {'email': 'nonexistent@test.com'}
        response = self.client.post(self.forgot_pass_url, form_data, follow=True)
        self.assertRedirects(response, self.forgot_pass_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("No user found with that email address.", str(messages[0]))


class RecoverPasswordViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            email='recover@test.com',
            password='oldpassword',
            id_number='456'
        )
        self.token_obj = Token.objects.create(
            token='resettoken123',
            type=TokenType.PASSWORD_RESET,
            user=self.user,
            expires_at=timezone.now() + timedelta(hours=2)
        )
        self.recover_url = reverse('recover-password', kwargs={'token': 'resettoken123'})

    def test_valid_token_and_form_resets_password(self):
        """
        This is a critical test. It ensures that after a successful password reset, the user's password is changed in
        the database and the one-time token is deleted. You can use user.check_password() to verify the new password
        without knowing the hash.
        """
        form_data = {
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(self.recover_url, form_data, follow=True)
        self.assertRedirects(response, reverse_lazy('login'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpassword123'))
        self.assertFalse(Token.objects.filter(token='resettoken123').exists())
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("Your password has been reset successfully.", str(messages[0]))

    def test_invalid_token_fails(self):
        invalid_url = reverse('recover-password', kwargs={'token': 'invalidtoken'})
        form_data = {
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(invalid_url, form_data, follow=True)
        self.assertRedirects(response, reverse_lazy('forgot-password'))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("The reset link is invalid or expired.", str(messages[0]))

    def test_expired_token_fails(self):
        # Make token expired
        self.token_obj.expires_at = self.token_obj.created_at - timedelta(seconds=1)
        self.token_obj.save()

        form_data = {
            'password1': 'newpassword123',
            'password2': 'newpassword123'
        }
        response = self.client.post(self.recover_url, form_data, follow=True)
        self.assertRedirects(response, reverse_lazy('forgot-password'))
        messages = list(get_messages(response.wsgi_request))
        self.assertIn("The reset link is invalid or expired.", str(messages[0]))
