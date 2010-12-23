import logging
from django import forms
from django.db.models import Q

from messages.forms import ComposeForm as MessagesComposeForm

from users.models import UserProfile

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):

    recipient = forms.CharField()

    def save(self, sender, parent_msg=None):
        recipient = self.cleaned_data['recipient']
        log.debug("Trying to send a message to %s" % (recipient,))
        try:
            profile = UserProfile.objects.get(
                Q(username=recipient) |
                Q(display_name=recipient) |
                Q(email=recipient),
            )
        except UserProfile.DoesNotExist:
            return
        self.cleaned_data['recipient'] = [profile.user]
        super(ComposeForm, self).save(sender, parent_msg)
