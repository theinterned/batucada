import logging

from messages.forms import ComposeForm as MessagesComposeForm

from drumbeatmail.fields import UserField

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):

    recipient = UserField()

    def save(self, sender, parent_msg=None):
        recipient = self.cleaned_data['recipient']
        log.debug("Trying to send a message to %s" % (recipient,))
        super(ComposeForm, self).save(sender, parent_msg)
