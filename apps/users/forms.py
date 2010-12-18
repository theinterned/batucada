from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from users.models import UserProfile

from drumbeat.utils import slug_validator


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = UserProfile

    def clean_username(self):
        """Make sure that username has no invalid characters."""
        username = self.cleaned_data['username']
        slug_validator(username, lower=False)
        return username

    def clean(self):
        """Ensure password and password_confirm match."""
        super(RegisterForm, self).clean()
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                self._errors['password_confirm'] = forms.util.ErrorList([
                    _('Passwords do not match.')])
        return data


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(
        label=_('Email Address:'),
        error_messages={'required': _('You must provide a valid email address.')})


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label=_("Password:"),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': ('Password is required.')})
    password_confirm = forms.CharField(
        label=_('Password (Again)'),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': _('Please confirm your password.')})
    username = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages={'required': _('Invalid username.')})
    token = forms.CharField(
        widget=forms.HiddenInput(),
        error_messages={'required': _('Invalid token value.')})

    def clean(self):
        """
        Ensure password and password_confirm match and that the token is valid
        and matches the provided user id.
        """
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise forms.ValidationError(_('Passwords do not match.'))
        if 'username' in data and 'token' in data:
            try:
                User.objects.get(username__exact=data['username'])
            except User.DoesNotExist:
                raise forms.ValidationError(_('User does not exist.'))
            # TODO - Check validity of token
        return data
