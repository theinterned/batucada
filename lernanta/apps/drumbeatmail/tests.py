from django.conf import settings
from django.contrib.auth.models import User

from users.models import create_profile
from drumbeatmail.forms import ComposeForm
from relationships.models import Relationship
from messages.models import Message

import test_utils


class TestDrumbeatMail(test_utils.TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en'
        django_user = User(username=self.test_username,
                           email=self.test_email)
        self.user = create_profile(django_user)
        self.user.set_password(self.test_password)
        self.user.save()

        django_user_two = User(username='anotheruser',
            email='test2@mozillafoundation.org')
        self.user_two = create_profile(django_user_two)
        self.user_two.set_password('testpassword')
        self.user_two.save()
        self.old_recaptcha_pubkey = settings.RECAPTCHA_PUBLIC_KEY
        self.old_recaptcha_privkey = settings.RECAPTCHA_PRIVATE_KEY
        settings.RECAPTCHA_PUBLIC_KEY, settings.RECAPTCHA_PRIVATE_KEY = '', ''

    def tearDown(self):
        settings.RECAPTCHA_PUBLIC_KEY = self.old_recaptcha_pubkey
        settings.RECAPTCHA_PRIVATE_KEY = self.old_recaptcha_privkey

    def test_messaging_user(self):
        print "From test: %s" % (self.user.user,)
        print "From test: %s" % (self.user_two.user,)
        form = ComposeForm(data={
            'recipient': self.user_two,
            'subject': 'Foo',
            'body': 'Bar',
        }, sender=self.user)
        self.assertTrue(form.is_bound)
        self.assertTrue(form.is_valid())

    def test_view_message(self):
        """Test user can view message in inbox."""
        Relationship(source=self.user, target_user=self.user_two).save()
        message = Message(
            sender=self.user_two.user,
            recipient=self.user.user,
            subject='test message subject',
            body='test message body')
        message.save()
        self.client.login(username=self.test_username,
                          password=self.test_password)
        response = self.client.get("/%s/messages/inbox/" % (self.locale,))
        self.assertContains(response, 'test message body')
