from django.contrib.auth.models import User
from django.db import IntegrityError
from django.test import TestCase, Client

from activity.models import Activity
from projects.models import Project, Link


class ProjectTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mozillafoundation.org'
    test_password = 'testpass'

    def setUp(self):
        self.client = Client()
        self.locale = 'en-US'
        self.client = Client()
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)

    def test_unique_slugs(self):
        """Test that each project will get a unique slug"""
        project = Project(
            name='My Cool Project',
            description='This project is awesome',
            call_to_action='Do Something',
            created_by=self.user,
        )
        project.save()
        self.assertEqual('my-cool-project', project.slug)
        project2 = Project(
            name='My Cool project',
            description='This project is awesome',
            call_to_action='This is all very familiar',
            created_by=self.user,
        )
        project2.save()
        self.assertEqual('my-cool-project1', project2.slug)

    def test_activity_firing(self):
        """Test that when a project is created, an activity is created."""
        self.assertEqual(0, Activity.objects.count())
        project = Project(
            name='My Cool Project',
            description='This project is awesome',
            call_to_action='Yawn',
            created_by=self.user,
        )
        project.save()
        self.assertEqual(1, Activity.objects.count())
        activity = Activity.objects.get(id=1)
        self.assertEqual(self.user, activity.actor)
        self.assertEqual(project, activity.obj)
        self.assertEqual(
            'http://drumbeat.org/activity/schema/1.0/project',
            activity.object_type)
        self.assertEqual(
            'http://drumbeat.org/activity/schema/1.0/create',
            activity.verb)

    def test_uniqueness_constraint(self):
        """Test that no two project links can have the same url."""
        project = Project(
            name='abc',
            description='def',
            call_to_action='123',
            created_by=self.user,
        )
        project.save()
        Link(title='My Blog', url='http://foo.com/', project=project).save()
        link2 = Link(title='Blah', url='http://foo.com/', project=project)
        self.assertRaises(IntegrityError, link2.save)
