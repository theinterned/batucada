from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.contrib.auth.models import User

from test_utils import TestCase

from activity.models import Activity
from activity.schema import verbs
from relationships.models import Relationship
from users.models import UserProfile, create_profile
from projects.models import Project


class RelationshipsTests(TestCase):

    test_users = [
        dict(username='test_one', email='test_one@mozillafoundation.org'),
        dict(username='test_two', email='test_two@mozillafoundation.org'),
    ]

    def setUp(self):
        """Create data for testing."""
        for user in self.test_users:
            django_user = User(**user)
            user = create_profile(django_user)
            user.set_password('testpass')
            user.save()
        (self.user_one, self.user_two) = UserProfile.objects.all()

    def test_unidirectional_user_relationship(self):
        """Test a one way relationship between two users."""
        # User 1 follows User 2
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_two,
        )
        relationship.save()
        self.assertEqual(self.user_one.following(), [self.user_two])

    def test_unique_user_constraint(self):
        """Test that a user can't follow another user twice."""
        # User 1 follows User 2
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_two,
        )
        relationship.save()

        # Try again
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_two,
        )
        self.assertRaises(IntegrityError, relationship.save)

    def test_unique_project_constraint(self):
        """Test that a user can't follow the same project twice."""
        project = Project(
            name='test project',
            short_description='for testing',
            long_description='for testing relationships',
        )
        project.save()
        relationship = Relationship(
            source=self.user_one,
            target_project=project,
        )
        relationship.save()
        relationship = Relationship(
            source=self.user_one,
            target_project=project,
        )
        self.assertRaises(IntegrityError, relationship.save)

    def test_narcissistic_user(self):
        """Test that one cannot follow oneself."""
        relationship = Relationship(
            source=self.user_one,
            target_user=self.user_one,
        )
        self.assertRaises(ValidationError, relationship.save)

    def test_bidirectional_relationship(self):
        """Test symmetric relationship."""
        Relationship(source=self.user_one, target_user=self.user_two).save()
        Relationship(source=self.user_two, target_user=self.user_one).save()

        rels_one = self.user_one.following()
        rels_two = self.user_two.following()

        self.assertTrue(self.user_one in rels_two)
        self.assertTrue(self.user_two not in rels_two)
        self.assertTrue(self.user_two in rels_one)
        self.assertTrue(self.user_one not in rels_one)

    def test_user_followers(self):
        """Test the followers method of the User model."""
        self.assertTrue(len(self.user_two.followers()) == 0)
        Relationship(source=self.user_one, target_user=self.user_two).save()
        self.assertTrue(len(self.user_two.followers()) == 1)
        self.assertEqual(self.user_one, self.user_two.followers()[0])

    def test_user_following(self):
        """Test the following method of the User model."""
        self.assertTrue(len(self.user_one.following()) == 0)
        Relationship(source=self.user_one, target_user=self.user_two).save()
        self.assertTrue(len(self.user_one.following()) == 1)
        self.assertEqual(self.user_two, self.user_one.following()[0])

    def test_user_is_following(self):
        """Test the is_following method of the User model."""
        self.assertFalse(self.user_one.is_following(self.user_two))
        Relationship(source=self.user_one, target_user=self.user_two).save()
        self.assertTrue(self.user_one.is_following(self.user_two))

    def test_activity_creation(self):
        """Test that an activity is created when a relationship is created."""
        self.assertEqual(0, Activity.objects.count())
        Relationship(source=self.user_one, target_user=self.user_two).save()
        activities = Activity.objects.all()
        self.assertEqual(1, len(activities))
        activity = activities[0]
        self.assertEqual(self.user_one, activity.actor)
        self.assertEqual(self.user_two, activity.target_object.target_user)
        self.assertEqual(verbs['follow'], activity.verb)
