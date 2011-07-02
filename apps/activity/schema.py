from django.utils.translation import ugettext_lazy as _

# Select new verbs an objects from
# http://activitystrea.ms/head/activity-schema.html
# as neccesary.

# a list of verbs defined in the activity schema
verbs = {
    'follow': 'http://activitystrea.ms/schema/1.0/follow',
    'join': 'http://activitystrea.ms/schema/1.0/join',
    'post': 'http://activitystrea.ms/schema/1.0/post',
    'update': 'http://activitystrea.ms/schema/1.0/update',
    'share': 'http://activitystrea.ms/schema/1.0/share',
    'receive': 'http://activitystrea.ms/schema/1.0/receive',
}

verbs_by_uri = {}
for key, value in verbs.iteritems():
    verbs_by_uri[value] = key

past_tense = {
    'follow': _('started following'),
    'join': _('joined'),
    'post': _('posted'),
    'update': _('updated'),
    'share': _('shared'),
    'received': _('received'),
}

# a list of base object types defined in the activity schema
object_types = {
    'person': 'http://activitystrea.ms/schema/1.0/person',
    'group': 'http://activitystrea.ms/schema/1.0/group',
    'article': 'http://activitystrea.ms/schema/1.0/article',
    'comment': 'http://activitystrea.ms/schema/1.0/comment',
    'status': 'http://activitystrea.ms/schema/1.0/status',
    'badge': 'http://activitystrea.ms/schema/1.0/badge',
}
