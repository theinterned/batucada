import logging

from django.conf import settings

from messages.forms import ComposeForm as MessagesComposeForm
from captcha import fields as captcha_fields

from drumbeatmail.fields import UserField

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):
    recipient = UserField()
    recaptcha = captcha_fields.ReCaptchaField()

    def __init__(self, sender=None, *args, **kwargs):
        self.sender = sender
        super(ComposeForm, self).__init__(*args, **kwargs)
        if not settings.RECAPTCHA_PRIVATE_KEY:
            del self.fields['recaptcha']


class ComposeReplyForm(MessagesComposeForm):
    recipient = UserField()

    def __init__(self, sender=None, *args, **kwargs):
        self.sender = sender
        super(ComposeReplyForm, self).__init__(*args, **kwargs)
