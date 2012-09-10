from django.test import Client
from django.contrib.auth.models import User

from courses import models as course_model

from test_utils import TestCase


class CourseTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mozillafoundation.org'
    test_password = 'testpass'

    test_title = "A test course"
    test_short_title = "Short title"
    test_plug = "Test plug"

    def setUp(self):
        self.client = Client()
        self.locale = 'en'
        self.course = course_model.create_course({
            "title": self.test_title,
            "short_title": self.test_short_title,
            "plug": self.test_plug,
        })
        #django_user = User(
        #    username=self.test_username,
        #    email=self.test_email,
        #)
        #self.user = create_profile(django_user)
        #self.user.set_password(self.test_password)
        #self.user.save()

    def test_course_creation(self):
        course = course_model.create_course({
            "title": "A test course",
            "short_title": "ATC 1",
            "plug": "This course is all about ABC",
        })

        self.assertTrue(not course == None)

        # test that about content was created
        about = course_model.get_content(course['about_uri'])
        self.assertTrue(not about == None)
        self.assertEqual(about['title'], "About")

        # test that cohort was created
        cohort = course_model.get_course_cohort(course['uri'])
        self.assertTrue(not cohort == None)

    def test_course_get(self):
        course = course_model.get_course(self.course['uri'])
        self.assertTrue('id' in course)
        self.assertTrue('uri' in course)
        self.assertTrue('title' in course)
        self.assertTrue('short_title' in course)
        self.assertTrue('about_uri' in course)
        self.assertTrue('slug' in course)
        self.assertTrue('plug' in course)
        self.assertTrue('creator' in course)
        self.assertTrue('content' in course)
        pass

    def test_add_content(self):
        pass

    def test_add_user(self):
        cohort = course_model.get_course_cohort(self.course['uri'])
        course_model.add_user_to_cohort(
            cohort['uri'], '/uri/user/bob', 'ORGANIZER')
        cohort2 = course_model.get_course_cohort(self.course['uri'])
        self.assertEqual(len(cohort['users']), len(cohort2['users'])-1)
