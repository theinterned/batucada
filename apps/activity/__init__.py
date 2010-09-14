from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _

from activity.models import Activity

class UnknownActivityError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Type(object):
    """Represent an entity defined in Atom Activity Base Schema."""

    past_tense = None
    ns = 'http://activitystrea.ms/schema/1.0/group'
    
    def __init__(self, name, past_tense=None):
        self.abbrev_name = name
        self.name = "%(namespace)s/%(name)s" % {
            'namespace': self.ns,
            'name': name
        }
        self.past_tense = past_tense

    @property
    def human_readable(self):
        """Generate a human readable form of this type."""
        term = self.name.split('/')[-1]
        if '-' in term:
            return ' '.join(map(lambda s: s.capitalize(), term.split('-')))
        return term.capitalize()
            
class DerivedType(Type):
    """Represent an entity defined by this site. Should extend a base type."""
    
    ns = 'http://drumbeat.org/activity/schema/1.0'

    def __init__(self, name, parent, past_tense=None):
        super(DerivedType, self).__init__(name, past_tense)
        self.parent = parent

object_types = [
    'article', 'audio', 'bookmark', 'comment', 'file', 'folder', 'group',
    'note', 'person', 'photo', 'photo-album', 'place', 'playlist', 'product',
    'review', 'service', 'status', 'video', 'event', 'song'
]
schema_object_types = {}
for object_type in object_types:
    schema_object_types[object_type] = Type(object_type)   

# Custom types 
schema_object_types.update({
    'project':  DerivedType('project', schema_object_types['group']),
})

schema_verbs = {
    'favorite':    Type('favorite', past_tense=_('favorited')),
    'follow':      Type('follow', past_tense=_('started following')),
    'like':        Type('like', past_tense=_('liked')),
    'make-friend': Type('make-friend', past_tense=_('friended')),
    'join':        Type('join', past_tense=_('joined')),
    'play':        Type('play', past_tense=_('played')),
    'post':        Type('post', past_tense=_('posted')),
    'save':        Type('save', past_tense=_('saved')),
    'share':       Type('share', past_tense=_('shared')),
    'tag':         Type('tag', past_tense=_('tagged')),
    'update':      Type('update', past_tense=_('updated')),
    'rsvp-yes':    Type('rsvp-yes', past_tense=_('is attending')),
    'rsvp-no':     Type('rsvp-no', past_tense=_('is not attending')),
    'rsvp-maybe':  Type('rsvp-maybe', past_tense=_('might be attending')),
}

# Custom verbs
schema_verbs.update({
    'create':      DerivedType('create',
                               schema_verbs['post'],
                               past_tense=_('created')),
})

def send(actor, verb, obj, target=None):
    if type(verb) == type(""):
        if verb not in schema_verbs:
            raise UnknownActivityError("Unknown verb: %s" % (verb,))
        verb = schema_verbs[verb]
    activity = Activity(
        actor=actor,
        verb=verb.abbrev_name,
        obj_content_type=ContentType.objects.get_for_model(obj),
        obj_id=obj.pk
    )
    if target:
        activity.target_content_type = ContentType.objects.get_for_model(target)
        activity.target_id = target.pk
    activity.save()
