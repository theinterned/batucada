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

        # NOTE: because we are using jinja2, we can't use the 
        # assertTemplateUsed method, so we have check for the
        # username element in the response body instead.
        self.assertContains(response, 'id_username', status_code=200)

    def test_authorized_request(self):
        """Authorized requests should land on a personalized dashboard."""
        self.client.login(username=self.test_username,
                          password=self.test_password)
        response = self.client.get('/%s/' % (self.locale,))
        self.assertContains(response, 'status_update', status_code=200)
        
    
