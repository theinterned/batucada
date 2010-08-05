from django import forms
from django.utils.translation import ugettext as _

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_('Email Address:'),
        error_messages={'required': _('You must provide a valid email address.')})

class PasswordResetForm(forms.Form):
    password = forms.CharField(
        label=_("Password:"),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': ('Password is required.')})
    password_confirm = forms.CharField(
        label=_('Password (Again)'),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': _('Please confirm your password.')})

    def clean(self):
        """Ensure password and password_confirm match."""
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise forms.ValidationError(_('Passwords do not match.'))
        return data
