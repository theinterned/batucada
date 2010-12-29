import logging

from messages.forms import ComposeForm as MessagesComposeForm

from drumbeatmail.fields import UserField

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):
    recipient = UserField()
