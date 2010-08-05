import hashlib

from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase

from forgetful.models import PasswordResetToken

class TestPasswordResets(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'
    
    def setUp(self):
        self.locale = 'en-US'
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

