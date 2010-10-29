from django.contrib.auth.models import User
from django.test import TestCase

class ProfileTests(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en-US'
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)
        
    def test_automatic_profile_creation(self):
        """Test that a user profile is created when a user is created."""
        profile = self.user.get_profile()
        self.assertTrue(profile is not None)
        self.assertEqual(self.user.first_name, profile.first_name)
        self.assertEqual(self.user.last_name, profile.last_name)

    def test_profile_field_syncing(self):
        """When we change certain fields in profiles, sync them with user."""
        profile = self.user.get_profile()
        profile.first_name = 'Jon'
        profile.last_name = 'Smith'
        profile.save()
        self.assertEqual(profile.first_name, self.user.first_name)
        self.assertEqual(profile.last_name, self.user.last_name)

    def test_profile_get_full_name(self):
        """Test ``get_full_name`` method on ``Profile``."""
        profile = self.user.get_profile()
        self.assertEqual(profile.get_full_name(), self.user.get_full_name())

    def test_profile_get_full_name_or_username(self):
        """Test ``get_full_name_or_username`` method on ``Profile``."""
        profile = self.user.get_profile()
        self.assertEqual(profile.get_full_name_or_username(), self.user.username)
        profile.first_name = 'Jon'
        profile.last_name = 'Smith'
        profile.save()
        self.assertEqual(profile.get_full_name_or_username(), 'Jon Smith')
        
