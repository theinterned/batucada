from django.utils.translation import ugettext as _

class ActivityTerm(object):
    schema_version = u'1.0'
    schema_base_uri = u'http://activitystrea.ms/schema'

    def iri(self):
        return u'%(base)s/%(version)s/%(name)s' % {
            'base': self.schema_base_uri,
            'version': self.schema_version,
            'name': self.name
        }

class ActivityVerb(ActivityTerm):
    def __init__(self, name, friendly):
        self.name = name
        self.friendly = friendly

class ActivityObject(ActivityTerm):
    def __init__(self, name):
        self.name = name
        
object_types = [
    'article', 'audio', 'bookmark', 'comment', 'file', 'folder', 'group',
    'note', 'person', 'photo', 'photo-album', 'place', 'playlist', 'product',
    'review', 'service', 'status', 'video', 'event', 'song'
]
verbs = {
    'favorite': ActivityVerb('favorite', _('favorited')),
    'follow': ActivityVerb('follow', _('followed')),
    'like': ActivityVerb('like', _('liked')),
    'make-friend': ActivityVerb('make-friend', _('friended')),
    'join': ActivityVerb('join', _('joined')),
    'play': ActivityVerb('play', _('played')),
    'post': ActivityVerb('post', _('posted')),
    'save': ActivityVerb('save', _('saved')),
    'share': ActivityVerb('share', _('shared')),
    'tag': ActivityVerb('tag', _('tagged')),
    'update': ActivityVerb('update', _('updated')),
    'rsvp-yes': ActivityVerb('rsvp-yes', _('is attending')),
    'rsvp-no': ActivityVerb('rsvp-no', _('is not attending')),
    'rsvp-maybe': ActivityVerb('rsvp-maybe', _('may be attending')),
}

schema = {
    'verbs': {},
    'objects': {}
}

for key, verb in verbs.items():
    schema['verbs'][key] = {
        'iri': verb.iri(),
        'friendly': verb.friendly
    }

for term in object_types:
    obj = ActivityObject(term)
    schema['objects'][term] = {
        'iri': obj.iri()
    }

def normalize(element):
    """
    Construct a verb or object-type URI from a simple term.
    e.g., photo => http://activitystrea.ms/schema/1.0/photo.
    """
    if element in verbs:
        return verbs[element].iri()
    elif element in object_types:
        return Object(element).iri()
    return element

def humanize_verb(verb):
    """
    Construct a human readable version of a verb to be used in a setance.
    e.g., post => posted, follow => started following
    """
    if verb in verbs:
        return verbs[verb].friendly
    return verb
