from django.contrib import auth
from django.contrib.auth.models import User
from django.test import Client, TestCase

from l10n.urlresolvers import reverse

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
        
    def test_unauthenticated_redirects(self):
        """Test that views requiring authentication redirect correctly."""
        paths = ('profile/edit/', 'profile/create/',
                 'profile/%s' % (self.test_username,))
        for path in paths:
            full = "/%s/%s" % (self.locale, path)
            response = self.client.get(full)
            self.assertRedirects(response, '/?next=%s' % (full,),
                                 status_code=302,
                                 target_status_code=301)        

    
