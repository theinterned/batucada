from django.test import Client
from django.contrib.auth.models import User

from l10n.urlresolvers import reverse
from users.models import UserProfile, create_profile
from activity.models import Activity
from projects.models import Project

from test_utils import TestCase


class ProjectTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mozillafoundation.org'
    test_password = 'testpass'

    def setUp(self):
        self.client = Client()
        self.locale = 'en'
        django_user = User(
            username=self.test_username,
            email=self.test_email,
        )
        self.user = create_profile(django_user)
        self.user.set_password(self.test_password)
        self.user.save()

    def test_unique_slugs(self):
        """Test that each project will get a unique slug"""
        project = Project(
            name='My Cool Project',
            short_description='This project is awesome',
            long_description='No really, its good',
        )
        project.save()
        self.assertEqual('my-cool-project', project.slug)
        project2 = Project(
            name='My Cool  Project',
            short_description='This project is awesome',
            long_description='This is all very familiar',
        )
        project2.save()
        self.assertEqual('my-cool-project-2', project2.slug)

    def test_activity_firing(self):
        """Test that when a project is created, an activity is created."""
        activities = Activity.objects.all()
        self.assertEqual(0, len(activities))
        project = Project(
            name='My Cool Project',
            short_description='This project is awesome',
            long_description='Yawn',
            created_by=self.user,
        )
        project.save()
        # expect 2 activities, a create and a follow
        activities = Activity.objects.all()
        self.assertEqual(2, len(activities))
        for activity in activities:
            self.assertEqual(self.user, activity.actor.user.get_profile())
            self.assertEqual(project, activity.project)
            self.assertTrue(activity.verb in (
                'http://activitystrea.ms/schema/1.0/post',
                'http://activitystrea.ms/schema/1.0/follow',
           ))


