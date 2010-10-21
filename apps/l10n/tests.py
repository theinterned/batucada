import re

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client, TestCase

from l10n.locales import LOCALES

class TestLocaleURLs(TestCase):
    def setUp(self):
        self.client = Client()
        
    def test_default_rewrites(self):
        """Test that the client gets what they ask for if it's supported."""
        for supported in LOCALES.keys():
            response = self.client.get('/', HTTP_ACCEPT_LANGUAGE=supported)
            self.assertRedirects(response, '/%s/' % (supported,),
                                 status_code=301)

    def test_specificity(self):
        """We support a more specific code than the general one sent."""
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertRedirects(response, '/en-US/', status_code=301)


    def test_close_match(self):
        """Client sends xx-YY, we support xx-ZZ. We give them xx-ZZ."""
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en-CA')
        self.assertRedirects(response, '/en-US/', status_code=301)

    def test_general(self):
        """
        If the client sends a specific locale that is unsupported, we
        should check for a more general match (xx-YY -> xx).
        """
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='de-AT')
        self.assertRedirects(response, '/de/', status_code=301)

    def test_unsupported_locale(self):
        """If locale is not supported, we should send them the default."""
        # if the default locale is not normalized, we'll get an additional 301
        default_locale = settings.LANGUAGE_CODE
        is_normalized = lambda l: re.match(r'[a-z]+-[A-Z]+', l) != None
        expected_target_code = is_normalized(default_locale) and 200 or 301
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='xx')
        self.assertRedirects(response,
                             '/%s/' % (default_locale,),
                             status_code=301,
                             target_status_code=expected_target_code)

    def test_normalized_case(self):
        """Accept-Language header is case insensitive."""
        response = self.client.get('/', HTTP_ACCEPT_LANGUAGE='en-us')
        self.assertRedirects(response, '/en-US/', status_code=301)

    
    def test_login_post_redirect(self):
        """Test that post requests are treated properly."""
        user = User.objects.create_user(
            'testuser', 'test@mozilla.com', 'testpass'
        )
        response = self.client.get('/de/login/')
        self.assertContains(response, 'csrfmiddlewaretoken')
        response = self.client.post('/de/login/', {
            'username': user.username,
            'password': 'testpass',
        })
        self.assertRedirects(response, '/de/', status_code=302)

