from django import forms
from django.db.models import Q
from django.utils.translation import ugettext_lazy as _

from users.models import UserProfile


class UserField(forms.Field):
    widget = forms.widgets.TextInput

    def clean(self, value):
        super(UserField, self).clean(value)
        if not value:
            return ''
        try:
            profile = UserProfile.objects.filter(deleted=False).get(
                Q(username=value) |
                Q(email=value),
            )
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                _(u'No such user with that username or email.'))

        # we return a list of ``User`` objects because that's what
        # the pinax messages application expects.
        return [profile.user]
