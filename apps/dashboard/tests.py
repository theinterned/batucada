from django.contrib.auth.models import User
from django.test import Client, TestCase

class DashboardTests(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en-US'
        self.client = Client()
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)

    def test_unauthorized_request(self):
        """Unauthorized requests should get a signin template."""
        response = self.client.get('/%s/' % (self.locale,))
        self.assertTemplateUsed(response, 'dashboard/splash.html')

    def test_authorized_request(self):
        """Authorized requests should land on a personalized dashboard."""
        self.client.login(username=self.test_username,
                          password=self.test_password)
        response = self.client.get('/%s/' % (self.locale,))
        self.assertTemplateUsed(response, 'dashboard/dashboard.html')
        
    
