import logging

from messages.forms import ComposeForm as MessagesComposeForm

from drumbeatmail.fields import UserField

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):
    recipient = UserField()

    def __init__(self, sender=None, *args, **kwargs):
        self.sender = sender
        super(ComposeForm, self).__init__(*args, **kwargs)
