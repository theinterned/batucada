from django.utils.translation import ugettext as _

schema_version = '1.0'
schema_base_uri = 'http://activitystrea.ms/schema'

human_readable_verbs = {
    'favorite': _('favorited'),
    'follow': _('started following'),
    'like': _('liked'),
    'make-friend': _('friended'),
    'join': _('joined'),
    'play': _('started playing'),
    'post': _('posted'),
    'save': _('saved'),
    'share': _('shared'),
    'tag': _('tagged'),
    'update': _('updated')
}

verbs = human_readable_verbs.keys()

object_types = [
    'article', 'audio', 'bookmark', 'comment', 'file', 'folder', 'group',
    'note', 'person', 'photo', 'photo-album', 'place', 'playlist', 'product',
    'review', 'service', 'status', 'video'
]

def normalize(element):
    if element not in verbs and element not in object_types:
        return element
    return u"%(base)s/%(version)s/%(element)s" % {
        'base': schema_base_uri,
        'version': schema_version,
        'element': element,
    }

qualified_objects = {}
for verb in verbs:
    qualified_objects[normalize(verb)] = verb
for object_type in object_types:
    qualified_objects[normalize(object_type)] = object_type

def humanize_verb(verb):
    if verb in human_readable_verbs:
        return human_readable_verbs[verb]
    if verb in qualified_objects:
        return human_readable_verbs[qualified_objects[verb]]
    return verb
