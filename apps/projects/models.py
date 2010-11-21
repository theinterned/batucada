import urllib

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify

from BeautifulSoup import BeautifulSoup

from relationships.models import followers


class Project(models.Model):
    """Placeholder model for projects."""
    object_type = 'http://drumbeat.org/activity/schema/1.0/project'
    generalized_object_type = 'http://activitystrea.ms/schema/1.0/group'
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    call_to_action = models.TextField()
    created_by = models.ForeignKey(User, related_name='projects')
    featured = models.BooleanField()
    template = models.TextField()
    css = models.TextField()

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('projects_show', (), {
            'slug': self.slug,
        })

    def save(self):
        """Make sure each project has a unique slug."""
        count = 1
        slug = slugify(self.name)
        self.slug = slug
        while True:
            existing = Project.objects.filter(slug=self.slug)
            if len(existing) == 0:
                break
            self.slug = slug + str(count)
            count += 1
        super(Project, self).save()

Project.followers = followers


class Link(models.Model):
    title = models.CharField(max_length=250)
    url = models.URLField()
    project = models.ForeignKey(Project)
    feed_url = models.URLField(editable=False, default='')

    class Meta:
        unique_together = ('project', 'url',)

    def save(self, *args, **kwargs):
        self.feed_url = self._get_syndication_url()
        super(Link, self).save(*args, **kwargs)

    def _get_syndication_url(self):
        """
        Parse the contents of this link and return the first Atom
        or RSS feed URI we find.
        @TODO - Account for cases where multiple rel="alternate"
        link elements are found in the document.
        """
        contents = urllib.urlopen(self.url).read()
        soup = BeautifulSoup(contents)
        links = soup.head.findAll('link')

        # BeautifulSoup instances are not actually dictionaries, so
        # we can't use the more proper 'key in dict' syntax and
        # must instead use the deprecated 'has_key()' method.
        alternate = [link for link in links
                     if link.has_key('rel') and link['rel'] == 'alternate']
        atom = [link['href'] for link in alternate
                if (link.has_key('href') and link.has_key('type')
                    and link['type'] == 'application/atom+xml')]

        # we prefer atom to rss
        if atom:
            return atom[0]
        rss = [link['href'] for link in links
               if (link.has_key('href') and link.has_key('type')
                   and link['type'] == 'application/rss+xml')]
        if rss:
            return rss[0]

        return None


def project_creation_handler(sender, **kwargs):
    project = kwargs.get('instance', None)
    created = kwargs.get('created', False)

    if not created or not isinstance(project, Project):
        return

    try:
        import activity
        activity.send(project.created_by, 'create', project)
    except ImportError:
        return

post_save.connect(project_creation_handler, sender=Project)
