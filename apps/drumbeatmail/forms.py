import logging

from django import forms

from messages.forms import ComposeForm as MessagesComposeForm

from users.models import UserProfile
from projects.models import Project
from drumbeatmail.fields import UserField

log = logging.getLogger(__name__)


class ComposeForm(MessagesComposeForm):
    recipient = UserField()

    def __init__(self, sender=None, *args, **kwargs):
        self.sender = sender
        super(ComposeForm, self).__init__(*args, **kwargs)

    def check_valid_recipient(self, recipient):
        """Check that the recipient is a follower of the sender."""
        try:
            user = UserProfile.objects.get(user=recipient)
        except UserProfile.DoesNotExist:
            log.debug("Non existant user: %s" % (recipient,))
            return False
        if self.sender in user.following():
            return True
        projects = Project.objects.filter(created_by=self.sender)
        following = user.following(model=Project)
        return any([p in following for p in projects])

    def clean_recipient(self):
        """Make sure that recipient follows sender or one of their projects."""
        valid = any(map(self.check_valid_recipient,
                        self.cleaned_data['recipient']))
        if not valid:
            raise forms.ValidationError(
                'One or more recipient is not following you.')
        return self.cleaned_data['recipient']
