from django.test import Client
from django.contrib.auth.models import User

from replies.models import PageComment
from users.models import create_profile
from projects.models import Project, Participation
from content.models import Page

from test_utils import TestCase


class RepliesViewsTests(TestCase):

    test_username = 'testuser'
    test_email = 'test@p2pu.org'
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

        self.project = Project(name='Reply Project',
            short_description='This project is to test replies',
            long_description='No really, its good',
        )
        self.project.save()
        
        participation = Participation(project=self.project,
            user=self.user, organizing=True)
        participation.save()
        
        self.page = Page(author=self.user,
            project=self.project,
            title='task title',
            sub_header='Tagline',
            content='Content',
            index=2)
        self.page.save()

    def test_comment(self):
        data = {
            'content': 'This is a comment',
        }
        self.client.login(username=self.test_username,
            password=self.test_password)
        comment_url = '/{0}/comments/create/page/content/{1}/project/projects/{2}/'.format(self.locale, self.page.id, self.project.id)
        response = self.client.post(comment_url, data)

        redirect_url = '/{0}/comments/1/'.format(self.locale)
        self.assertRedirects(response, redirect_url, target_status_code=302)
            
        comments = PageComment.objects.all()
        self.assertEquals(comments.count(), 1)

    def test_repy(self):

        comment = PageComment()
        comment.page_object = self.page
        comment.scope_object = self.project
        comment.author = self.user
        comment.content = "blah blah"
        comment.save()

        self.client.login(username=self.test_username, password=self.test_password)

        # post reply
        data = { 'content': 'This is a reply' }
        reply_url = '/{0}/comments/{1}/reply/'.format(self.locale, comment.id)
        response = self.client.post(reply_url, data)
            
        comments = PageComment.objects.all()
        self.assertEquals(comments.count(), 2)       


    def test_reply_by_email(self):
        # post a comment
        comment = PageComment()
        comment.page_object = self.page
        comment.scope_object = self.project
        comment.author = self.user
        comment.content = "blah blah"
        comment.save()
        
        data = {
            u'from': [u'Testing <test@p2pu.org>'],
            u'text': [u'Maybe this time\n'],
        }

        response = self.client.post('/{0}/comments/{1}/email_reply/'.format(self.locale, comment.id), data)
        self.assertEqual(response.status_code, 200)

        comments = PageComment.objects.all()
        self.assertEquals(comments.count(), 2)        
