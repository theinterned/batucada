from django.utils.http import urlquote
from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from messages.models import Message

def messages(request):
    if request.user.is_authenticated():
        messages = Message.objects.select_related('sender').filter(
            recipient=request.user,
            recipient_deleted_at__isnull=True)[:3]
        return {'preview_messages': messages}
    else:
        return {}

def login_with_redirect(request):
    login_url = settings.LOGIN_URL
    path = urlquote(request.get_full_path())
    url = '%s?%s=%s' % (settings.LOGIN_URL, REDIRECT_FIELD_NAME, path)
    return {'login_url': url}    
