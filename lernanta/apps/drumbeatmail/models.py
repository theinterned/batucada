from django.db.models.signals import post_save
from django.contrib.sites.models import Site

from l10n.urlresolvers import reverse
from messages.models import Message
from users.tasks import SendUserEmail
from preferences.models import AccountPreferences
from l10n.models import localize_email
from richtext import clean_html

import logging

log = logging.getLogger(__name__)


def message_sent_handler(sender, **kwargs):
    message = kwargs.get('instance', None)
    created = kwargs.get('created', False)
    if not created or not isinstance(message, Message):
        return
    recipient = message.recipient.get_profile()
    preferences = AccountPreferences.objects.filter(user=recipient,
       key='no_email_message_received')
    for preference in preferences:
        if preference.value:
            return
    sender = message.sender.get_profile()
    reply_url = reverse('drumbeatmail_reply', kwargs={'message': message.pk})
    msg_body = clean_html('rich', message.body)
    context = {
        'sender': sender,
        'message': msg_body,
        'domain': Site.objects.get_current().domain,
        'reply_url': reply_url,
    }
    subjects, bodies = localize_email(
        'drumbeatmail/emails/direct_message_subject.txt',
        'drumbeatmail/emails/direct_message.txt', context)
    SendUserEmail.apply_async((recipient, subjects, bodies))

post_save.connect(message_sent_handler, sender=Message,
    dispatch_uid='drumbeatmail_message_sent_handler')
