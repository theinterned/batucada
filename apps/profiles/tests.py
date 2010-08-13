from django.contrib.auth.models import User
from django.test import TestCase

from profiles.models import ContactNumber, Link
from profiles.forms import ContactNumberForm

class ProfileTests(TestCase):

    test_username = 'testuser'
    test_password = 'testpassword'
    test_email = 'test@mozillafoundation.org'

    def setUp(self):
        self.locale = 'en-US'
        self.user = User.objects.create_user(self.test_username,
                                             self.test_email,
                                             self.test_password)
        
    def test_automatic_profile_creation(self):
        """Test that a user profile is created when a user is created."""
        profile = self.user.get_profile()
        self.assertTrue(profile is not None)
        self.assertEqual(self.user.first_name, profile.first_name)
        self.assertEqual(self.user.last_name, profile.last_name)

    def test_profile_field_syncing(self):
        """When we change certain fields in profiles, sync them with user."""
        profile = self.user.get_profile()
        profile.first_name = 'Jon'
        profile.last_name = 'Smith'
        profile.save()
        self.assertEqual(profile.first_name, self.user.first_name)
        self.assertEqual(profile.last_name, self.user.last_name)

    def test_profile_get_full_name(self):
        """Test ``get_full_name`` method on Profile."""
        profile = self.user.get_profile()
        self.assertEqual(profile.get_full_name(), self.user.get_full_name())

    def test_adding_contactnumber(self):
        """Add contact numbers to a profile."""
        profile = self.user.get_profile()
        ContactNumber(profile=profile, number='416-555-5555',
                      label='Home').save()
        self.assertEqual(1, profile.contactnumber_set.count())
        numbers = profile.contactnumber_set.all()
        self.assertEqual('Home', numbers[0].label)
        self.assertEqual('416-555-5555', numbers[0].number)

    def test_removing_contactnumber(self):
        """Delete contact number from profile."""
        ContactNumber(profile=self.user.get_profile(), number='416-555-5555',
                      label='Home').save()
        self.assertEqual(1, self.user.get_profile().contactnumber_set.count())
        self.user.get_profile().contactnumber_set.all()[0].delete()
        self.assertEqual(0, self.user.get_profile().contactnumber_set.count())

    def test_adding_bad_contactnumber(self):
        """Try adding an invalid contact number through the ``Form`` object."""
        invalid = ('abcd', '416-abc-5555', '41a-555-5555', '416-555-555a',
                   '416-555-5555a', '416+555+5555',
                   '123456789101112131415161718')
        valid = ('(416)555 5555', '416-555-5555', '011-44-3233-4444',
                 '(416)  5555-555555')
        validate_form = lambda n: ContactNumberForm(data={
            'number': n,
            'label' : 'Home',
            'profile': self.user.get_profile()
        }).is_valid()
        for number in invalid:
            self.assertFalse(validate_form(number))
        for number in valid:
            self.assertTrue(validate_form(number))

    def test_adding_links(self):
        """Test adding a couple of links to a profile."""
        Link(
            profile=self.user.get_profile(),
            title='This is my excellent blog',
            uri='http://mostawesomeblog.org'
        ).save()
        self.assertEqual(1, self.user.get_profile().link_set.count())
        Link(
            profile=self.user.get_profile(),
            title='I dig the twitter',
            uri='http://twitter.com/test'
        ).save()
        self.assertEqual(2, self.user.get_profile().link_set.count())
    
    def test_deleting_links(self):
        """Test removing links."""
        Link(profile=self.user.get_profile(), title='Blah', uri='Blah').save()
        self.assertEqual(1, self.user.get_profile().link_set.count())
        self.user.get_profile().link_set.all()[0].delete()
        self.assertEqual(0, self.user.get_profile().link_set.count())
