import hashlib

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, Client

from forgetful.models import PasswordResetToken

class TestPasswordResets(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'
    
    def setUp(self):
        self.locale = 'en-US'
        self.client = Client()
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)

    def test_reset_token_uniqueness_constraint(self):
        """Test that only one password reset token can exist per user."""
        token = PasswordResetToken(user=self.user, token='abcdef')
        token.save()
        token_two = PasswordResetToken(user=self.user, token='fedcba')
        self.assertRaises(IntegrityError, token_two.save)
        token.delete()
        token_two.save()

    def test_automatic_reset_token_hashing(self):
        """Password reset tokens should be hashed, transparent to the caller."""
        token_string = 'abcdef'
        token = PasswordResetToken(user=self.user, token=token_string)
        token.save()
        self.assertNotEqual(token_string, token.token)
        (algo, salt, hsh) = token.token.split('$')
        expected = hashlib.sha1(salt + token_string).hexdigest()
        self.assertEqual(expected, hsh)

    def test_check_reset_token(self):
        """Verify that password reset tokens can be compared reliably."""
        token_string = 'abcdef'
        token = PasswordResetToken(user=self.user, token=token_string)
        token.save()
        self.assertTrue(token.check_token(token_string))
        self.assertFalse(token.check_token('fedcba'))

    def test_password_reset_form_invalid_token(self):
        """Test that invalid reset form tokens are rejected."""
        new_password = 'foobar'
        error_message = 'Sorry, invalid username or token'
        PasswordResetToken(user=self.user, token='abcdef')
        path = '/%s/reset/%s/%s/' % (self.locale, 'badtoken', self.user.username)
        response = self.client.get(path)
        self.assertContains(response, error_message)
        response = self.client.post(path, {
            'password': new_password, 'password_confirm': new_password
        })
        self.assertContains(response, error_message)

    def test_password_reset_form_valid_token(self):
        """Test that valid reset tokens are accepted."""
        error_message = 'Sorry, invalid username or token'
        token_string = 'abcdef'
        new_password = 'foobar'
        PasswordResetToken(user=self.user, token=token_string).save()
        path = '/%s/reset/%s/%s/' % (self.locale, token_string, self.user.username)
        response = self.client.get(path)
        self.assertNotContains(response, error_message)
        response = self.client.post(path, {
            'password': new_password, 'password_confirm': new_password
        })
        self.assertRedirects(response, '/', status_code=302,
                             target_status_code=301)
        # refresh user object
        self.user = User.objects.get(username__exact=self.user.username)
        self.assertTrue(self.user.check_password(new_password))

    def test_password_reset_form_invalid_username(self):
        """Test that invalid usernames are rejected."""
        token_string = 'abcdef'
        error_message = 'Sorry, invalid username or token'
        new_password = 'foobar'
        PasswordResetToken(user=self.user, token=token_string).save()
        path = '/%s/reset/%s/%s/' % (self.locale, token_string, 'foo')
        response = self.client.get(path)
        self.assertContains(response, error_message)
        response = self.client.post(path, {
            'password': new_password, 'password_confirm': new_password
        })
        self.assertContains(response, error_message)
