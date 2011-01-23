from django.test import Client

from drumbeat.utils import get_partition_id
from users.models import UserProfile

from test_utils import TestCase


class TestLogins(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en-US'
        self.client = Client()
        self.user = UserProfile(username=self.test_username,
                                email=self.test_email)
        self.user.set_password(self.test_password)
        self.user.save()
        self.user.create_django_user()

    def test_authenticated_redirects(self):
        """Test that authenticated users are redirected in specific views."""
        self.client.login(username=self.test_username,
                          password=self.test_password)
        paths = ('login/', 'register/',
                 'confirm/123456/username/',
                 'confirm/resend/username/')
        for path in paths:
            full = "/%s/%s" % (self.locale, path)
            response = self.client.get(full)
            print response
            self.assertRedirects(response, '/', status_code=302,
                                 target_status_code=301)
        self.client.logout()

    def test_unauthenticated_redirects(self):
        """Test that anonymous users are redirected for specific views."""
        paths = ('logout/', 'profile/edit/', 'profile/edit/image/')
        for path in paths:
            full = "/%s/%s" % (self.locale, path)
            response = self.client.get(full)
            expected = "/%s/" % (self.locale,)
            self.assertRedirects(response, expected, status_code=302,
                                 target_status_code=200)

    def test_login_post(self):
        """Test logging in."""
        path = "/%s/login/" % (self.locale,)
        response = self.client.post(path, {
            'username': self.test_username,
            'password': self.test_password,
        })
        self.assertRedirects(response, '/', status_code=302,
                             target_status_code=301)
        # TODO - Improve this so it doesn't take so many redirects to get a 200
        response2 = self.client.get(response["location"])
        response3 = self.client.get(response2["location"])
        response4 = self.client.get(response3["location"])
        self.assertContains(response4, 'id="dashboard"')
        self.client.logout()

        response5 = self.client.post(path, {
            'username': 'nonexistant',
            'password': 'password',
        })
        self.assertContains(response5, 'id="id_username"')

    def test_login_next_param(self):
        """Test that user is redirected properly after logging in."""
        path = "/%s/login/?next=/%s/profile/edit/" % (self.locale, self.locale)
        response = self.client.post(path, {
            'username': self.test_username,
            'password': self.test_password,
        })
        self.assertEqual(
            "http://testserver/%s/profile/edit/" % (self.locale,),
            response["location"],
        )

    def test_login_next_param_header_injection(self):
        """Test that we can't inject headers into response with next param."""
        path = "/%s/login/" % (self.locale,)
        next_param = "foo\r\nLocation: http://example.com"
        response = self.client.post(path + "?next=%s" % (next_param), {
            'username': self.test_username,
            'password': self.test_password,
        })
        # we expect the header to be urlencoded before being sent.
        self.assertTrue('login/foo%0D%0ALocation' in response['location'])
        self.assertNotEqual('http://example.com', response['location'])

    def test_registration_opt_in(self):
        """Test account registration."""
        path = "/%s/register/" % (self.locale,)
        params = {
            'display_name': 'Joe User',
            'username': 'joeuser',
            'password': 'abcdefghijklmno1',
            'password_confirm': 'abcdefghijklmno1',
            'email': 'joe@mozilla.com',
        }
        response = self.client.post(path, params)
        self.assertContains(response, 'You must agree to the licensing terms')
        params['policy_optin'] = 'on'
        response = self.client.post(path, params)
        self.assertEqual(response.status_code, 302)

    def test_profile_image_directories(self):
        """Test that we partition image directories properly."""
        for i in range(1, 1001):
            p_id = get_partition_id(i)
            self.assertEqual(1, p_id)
        for i in range(1001, 2001):
            p_id = get_partition_id(i)
            self.assertEqual(2, p_id)
        for i in range(10001, 11001):
            p_id = get_partition_id(i)
            self.assertEqual(11, p_id)
        self.assertEqual(12, get_partition_id(11002))
