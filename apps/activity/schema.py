from django.utils.translation import ugettext_lazy as _

# a list of verbs defined in the activity schema
verbs = {
    'favorite': 'http://activitystrea.ms/schema/1.0/favorite',
    'follow': 'http://activitystrea.ms/schema/1.0/follow',
    'like': 'http://activitystrea.ms/schema/1.0/like',
    'make-friend': 'http://activitystrea.ms/schema/1.0/make-friend',
    'join': 'http://activitystrea.ms/schema/1.0/join',
    'play': 'http://activitystrea.ms/schema/1.0/play',
    'post': 'http://activitystrea.ms/schema/1.0/post',
    'save': 'http://activitystrea.ms/schema/1.0/save',
    'share': 'http://activitystrea.ms/schema/1.0/share',
    'tag': 'http://activitystrea.ms/schema/1.0/tag',
    'update': 'http://activitystrea.ms/schema/1.0/update',
    'rsvp-yes': 'http://activitystrea.ms/schema/1.0/rsvp-yes',
    'rsvp-no': 'http://activitystrea.ms/schema/1.0/rsvp-no',
    'rsvp-maybe': 'http://activitystrea.ms/schema/1.0/rsvp-maybe',
    'delete': 'http://activitystrea.ms/schema/1.0/delete',
}

verbs_by_uri = {}
for key, value in verbs.iteritems():
    verbs_by_uri[value] = key

past_tense = {
    'favorite': _('favorited'),
    'follow': _('started following'),
    'like': _('liked'),
    'make-friend': _('is now friends with'),
    'join': _('joined'),
    'play': _('played'),
    'post': _('posted'),
    'save': _('saved'),
    'share': _('shared'),
    'tag': _('tagged'),
    'update': _('updated'),
    'rsvp-yes': _('is attending'),
    'rsvp-no': _('is not attending'),
    'rsvp-maybe': _('might be attending'),
    'delete': _('deleted'),
}

# a list of base object types defined in the activity schema
object_types = {
    'article': 'http://activitystrea.ms/schema/1.0/article',
    'audio': 'http://activitystrea.ms/schema/1.0/audio',
    'bookmark': 'http://activitystrea.ms/schema/1.0/bookmark',
    'comment': 'http://activitystrea.ms/schema/1.0/comment',
    'file': 'http://activitystrea.ms/schema/1.0/file',
    'folder': 'http://activitystrea.ms/schema/1.0/folder',
    'group': 'http://activitystrea.ms/schema/1.0/group',
    'note': 'http://activitystrea.ms/schema/1.0/note',
    'person': 'http://activitystrea.ms/schema/1.0/person',
    'photo': 'http://activitystrea.ms/schema/1.0/photo',
    'photo-album': 'http://activitystrea.ms/schema/1.0/photo-album',
    'place': 'http://activitystrea.ms/schema/1.0/place',
    'playlist': 'http://activitystrea.ms/schema/1.0/playlist',
    'product': 'http://activitystrea.ms/schema/1.0/product',
    'review': 'http://activitystrea.ms/schema/1.0/review',
    'service': 'http://activitystrea.ms/schema/1.0/service',
    'status': 'http://activitystrea.ms/schema/1.0/status',
    'video': 'http://activitystrea.ms/schema/1.0/video',
    'event': 'http://activitystrea.ms/schema/1.0/event',
}
