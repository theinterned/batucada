import os
import urllib2
import feedparser
from StringIO import StringIO

from django_push.subscriber.models import Subscription
from django.contrib.auth.models import User

from links import utils
from links.tasks import HandleNotification
from links.models import Link

from test_utils import TestCase
from activity.models import Activity
from users.models import create_profile


def mock_open(r):
    return urllib2.HTTPError('request', 204, 'no-op', {}, StringIO(''))

urllib2.urlopen = mock_open
urllib2.Request = lambda x, y, z: 'request'


class TestLinkParsing(TestCase):

    def setUp(self):
        self.fixtures = {}
        root = os.path.dirname(os.path.abspath(__file__))
        fixture_dir = os.path.join(root, 'fixtures')
        for f in os.listdir(fixture_dir):
            self.fixtures[f] = file(os.path.join(fixture_dir, f)).read()

        django_user = User(username='testuser',
                           email='test@mozillafoundation.org')
        self.user = create_profile(django_user)
        self.user.set_password('testpassword')
        self.user.save()

    def test_feed_parser(self):
        """Perform a straightforward test of the feed url parser."""
        html = """
        <html>
        <head>
          <title>Test HTML</title>
          <link rel="alternate" type="application/rss+xml"
             href="http://example.com/rss">
        </head>
        <body>
           <h1>Test</h1>
        </body>
        </html>
        """
        feed_url = utils.parse_feed_url(html)
        self.assertEqual('http://example.com/rss', feed_url)

    def test_feed_parser_multiple_alternates(self):
        """Test that given HTML with multiple feeds, the first is returned."""
        html = self.fixtures['selfhosted_wp_blog.html']
        feed_url = utils.parse_feed_url(html)
        self.assertEqual('http://blog.eval.ca/feed/', feed_url)

    def test_preference_of_atom(self):
        """Test that provided with RSS and Atom feeds, Atom comes out."""
        html = """
        <html>
          <head>
            <title>Test</title>
            <link rel="alternate" type="application/rss+xml"
              href="http://foo.com/rss" />
            <link rel="alternate" type="application/rss+xml"
              href="http://foo.com/comments/rss" />
            <link rel="alternate" type="application/atom+xml"
              href="http://foo.com/atom" />
            <link rel="alternate" type="application/atom+xml"
              href="http://foo.com/comments/atom" />
          </head>
        </html>
        """
        feed_url = utils.parse_feed_url(html)
        self.assertEqual('http://foo.com/atom', feed_url)

    def test_invalid_markup(self):
        """Test that parsing invalid markup works."""
        html = """<html><head><link rel="alternate" type="application/atom+xml"
        href="http://foo.com/atom"><body></html>"""
        feed_url = utils.parse_feed_url(html)
        self.assertEqual('http://foo.com/atom', feed_url)

    def test_hub_parser(self):
        """Test that we find a hub for a sample hosted WP rss feed."""
        rss = self.fixtures['rss_hub.rss']
        hub_url = utils.parse_hub_url(rss)
        self.assertEqual('http://commonspace.wordpress.com/?pushpress=hub',
                         hub_url)

    def test_hub_parser_no_hub(self):
        """Test that an rss feed with no hub declaration is returned as None"""
        rss = self.fixtures['rss_no_hub.rss']
        hub_url = utils.parse_hub_url(rss)
        self.assertEqual(None, hub_url)

    def test_hub_discovery(self):
        """Using a google buzz profile, find the atom feed and the hub url."""
        html = self.fixtures['buzz_profile.html']
        feed_url = utils.parse_feed_url(html)
        self.assertEqual(
            'https://www.googleapis.com/buzz/v1/' +
            'activities/115398213828503499359/@public',
            feed_url)
        atom = self.fixtures['buzz_profile.atom']
        hub_url = utils.parse_hub_url(atom)
        self.assertEqual(
            'http://pubsubhubbub.appspot.com/',
            hub_url)

    def test_normalize_url(self):
        url = '/feed.rss'
        base_url = 'http://example.com'
        self.assertEqual('http://example.com/feed.rss',
                        utils.normalize_url(url, base_url))

    def test_normalize_url_two_slashes(self):
        url = '/feed.rss'
        base_url = 'http://example.com/'
        self.assertEqual('http://example.com/feed.rss',
                         utils.normalize_url(url, base_url))

    def test_normalize_url_trailing_slash_base(self):
        url = 'feed.rss'
        base_url = 'http://example.com/'
        self.assertEqual('http://example.com/feed.rss',
                         utils.normalize_url(url, base_url))

    def test_normalize_url_no_slashes(self):
        url = 'feed.rss'
        base_url = 'http://example.com'
        self.assertEqual('http://example.com/feed.rss',
                         utils.normalize_url(url, base_url))

    def test_normalize_url_good_url(self):
        url = 'http://example.com/atom'
        self.assertEqual(url, utils.normalize_url(url, 'http://example.com'))

    def test_notification(self):
        sub = Subscription.objects.create(
            hub='http://blah/', topic='http://blah')
        Link.objects.create(
            name='foo',
            url='http://blah/',
            subscription=sub,
            user=self.user)
        count = Activity.objects.count()
        test_feed_data = """<?xml version='1.0'?>
        <feed xmlns='http://www.w3.org/2005/Atom'
              xmlns:activity='http://activitystrea.ms/spec/1.0/'
              xml:lang='en-US'>
            <link type='text/html' rel='alternate' href='http://example.com'/>
            <link type='application/atom+xml' rel='self'
                href='http://example.com/feed/'/>
            <entry>
               <activity:verb>
                 http://activitystrea.ms/schema/1.0/follow
               </activity:verb>
               <activity:object-type>
                 http://activitystrea.ms/schema/1.0/person
               </activity:object-type>
               <link type='text/html' rel='alternate'
                   href='http://example.com/activity/'/>
               <title>Jane started following John</title>
            </entry>
        </feed>"""
        parsed = feedparser.parse(test_feed_data)
        handler = HandleNotification()
        handler.run(parsed, sub)
        self.assertEqual(Activity.objects.count(), count + 1)
