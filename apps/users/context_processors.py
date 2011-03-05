from django.utils.http import urlquote
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from messages.models import Message
from l10n.urlresolvers import reverse

def messages(request):
    if request.user.is_authenticated():
        messages = Message.objects.select_related('sender').filter(
            recipient=request.user,
            recipient_deleted_at__isnull=True)[:3]
        return {'preview_messages': messages}
    else:
        return {}

def login_with_redirect_url(request):
    path = urlquote(request.get_full_path())
    url = '%s?%s=%s' % (reverse('users_login'), REDIRECT_FIELD_NAME, path)
    return {'login_with_redirect_url': url} 
