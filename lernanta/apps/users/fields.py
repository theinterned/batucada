from django import forms
from django.core import urlresolvers
from django.conf import settings

from drumbeat.utils import slug_validator
from django.utils.translation import ugettext_lazy as _


class UsernameField(forms.Field):
    widget = forms.widgets.TextInput(attrs={'autocomplete': 'off'})

    def clean(self, value):
        super(UsernameField, self).clean(value)
        slug_validator(value, lower=False)
        try:
            func, args, kwargs = urlresolvers.resolve("/%s/" % (value,))
            if callable(func) and args == ():
                if 'username' not in kwargs.keys():
                    raise forms.ValidationError(
                        _('Please choose another username.'))
        except urlresolvers.Resolver404:
            pass
        if value in settings.INVALID_USERNAMES:
            raise forms.ValidationError(_('Please choose another username.'))
        return value
