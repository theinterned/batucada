from django.core import mail
from test_utils import TestCase

from relationships.models import Relationship
from users.models import UserProfile
from preferences.models import AccountPreferences

class AccountPreferencesTests(TestCase):

    test_users = [
        dict(username='test_one', email='test_one@mozillafoundation.org'),
        dict(username='test_two', email='test_two@mozillafoundation.org'),
    ]

    def setUp(self):
        """Create data for testing."""
        for user in self.test_users:
            user = UserProfile(**user)
            user.set_password('testpass')
            user.save()
            user.create_django_user()
        (self.user_one, self.user_two) = UserProfile.objects.all()

    def test_new_follower_email_preference(self):
        """Test user is emailed when they get a new follower when that user wants to be emailed when they get a new follower."""
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_two,
        )
        relationship.save()
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].to, [self.user_two.email,])
    
    def test_no_new_follower_email_preference(self):
        """Test user is *not* emailed when they get a new follower when that user does *not* want to be emailed when they get a new follower."""
        AccountPreferences(user=self.user_two, key='no_email_new_follower', value=1).save()
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_two,
        )
        relationship.save()
        self.assertEquals(len(mail.outbox), 0)
    
