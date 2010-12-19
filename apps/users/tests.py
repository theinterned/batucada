from django.contrib.auth.models import User
from django.test import Client, TestCase


class TestLogins(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en-US'
        self.client = Client()
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)

    def test_authenticated_redirects(self):
        """Test that authenticated users are redirected in specific views."""
        self.client.login(username=self.test_username,
                          password=self.test_password)
        paths = ('login/', 'openid/login/', 'register/',
                 'openid/register/', 'forgot/')
        for path in paths:
            full = "/%s/%s" % (self.locale, path)
            response = self.client.get(full)
            self.assertRedirects(response, '/', status_code=302,
                                 target_status_code=301)
        self.client.logout()

    def test_next_get_parameter(self):
        """
        Test that upon successful login, users are sent a Location header
        with the value of the ``next`` GET parameter, if present.
        """
        path = '/%s/login/?next=/%s/profile/edit/' % (self.locale, self.locale)
        response = self.client.get(path)
        self.assertContains(response, '/%s/profile/edit/' % (self.locale,))
        response = self.client.post(path, {
            'username': self.test_username,
            'password': self.test_password,
            'next': '/%s/profile/edit/' % (self.locale,),
        })
        self.assertTrue(response.has_header('location'))
        self.assertEqual(response['location'],
                         'http://testserver/%s/profile/edit/' % (self.locale,))

    def test_header_injection_next_parameter(self):
        """
        Test that a user cannot inject content into the HTTP response headers
        through selectively formatted values of the ``next`` GET parameter.
        """
        path = '/%s/login/' % (self.locale,)
        qs = '?next=/%s/profile/edit/\n\nFoo' % (self.locale,)
        response = self.client.get(path + qs)
        self.assertContains(response, '/%s/profile/edit/' % (self.locale,))
        self.assertFalse(response.has_header('location'))

    def test_html_injection_next_parameter(self):
        """
        Test that a user cannot inject content into the HTML response
        through selectively formatted values of the ``next`` GET parameter.
        """
        path = '/%s/login/' % (self.locale,)
        qs = '?next=/%s/profile/edit/" /><blink>Damn!</blink>'
        response = self.client.get(path + qs)
        self.assertNotContains(response, '<blink>')
        self.assertContains(response, '&lt;blink&gt;')
