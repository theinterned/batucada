from django.test import Client
from django.contrib.auth.models import User

from users.models import create_profile
from projects.models import Project, Participation
from content.models import Page

from test_utils import TestCase


class PageTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@mozillafoundation.org'
    test_password = 'testpass'

    def setUp(self):
        self.client = Client()
        self.locale = 'en'
        django_user = User(
            username=self.test_username,
            email=self.test_email,
        )
        self.user = create_profile(django_user)
        self.user.set_password(self.test_password)
        self.user.save()
        self.project = Project(name='My Cool Project',
            short_description='This project is awesome',
            long_description='No really, its good',
        )
        self.project.save()
        participation = Participation(project=self.project,
            user=self.user, organizing=True)
        participation.save()
        for i in xrange(3):
            page = Page(author=self.user,
                project=self.project,
                title='Old Title %s' % i,
                sub_header='Old Tagline %s' % i,
                content='Old Content %s' % i,
                index=2*(i+1))
            page.save()

    def test_page_reorder(self):
        self.client.login(username=self.test_username,
            password=self.test_password)

        #slugs = [slug[0] for slug in self.project.pages.values_list('slug')]
        slug1 = self.project.pages.all()[0].slug
        slug2 = self.project.pages.all()[1].slug
        slug3 = self.project.pages.all()[2].slug

        data = { 'tasks[]':[slug1, slug3, slug2] }

        reorder_url = "/{0}/groups/{1}/content/index/reorder/".format(
            self.locale, self.project.slug)
        response = self.client.post(reorder_url, data)
        self.assertEqual(response.status_code, 200)

        page1 = self.project.pages.get(slug=slug1)
        page2 = self.project.pages.get(slug=slug2)
        page3 = self.project.pages.get(slug=slug3)

        self.assertTrue(page1.index < page3.index)
        self.assertTrue(page3.index < page2.index)
