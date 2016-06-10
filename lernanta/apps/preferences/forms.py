from django import forms
from users.models import UserProfile
from django.utils.translation import ugettext as _
import re
from users.blacklist import passwords as blacklisted_passwords

from users import drupal


class EmailEditForm(forms.ModelForm):
    email_confirm = forms.EmailField(max_length=75)

    def __init__(self, username, *args, **kwargs):
        super(EmailEditForm, self).__init__(*args, **kwargs)
        self.username = username

    class Meta:
        model = UserProfile
        fields = ('email',)

    def clean(self):
        super(EmailEditForm, self).clean()
        msg = _('That email address is register under a different username.')
        data = self.cleaned_data
        if 'email' in data:
            drupal_user = drupal.get_user(data['email'])
            if drupal_user and self.username != drupal_user.name:
                self._errors['email'] = forms.util.ErrorList([msg])
            if data['email'] != data.get('email_confirm', data['email']):
                self._errors['email_confirm'] = forms.util.ErrorList([
                    _('Email addresses do not match.')])
        return data


def check_password_complexity(password):
    message = _('Password must be at least 8 characters long ')
    message += _('and contain both numbers and letters.')
    if len(password) < 8 or not (
        re.search('[A-Za-z]', password) and re.search('[0-9]', password)):
        return message
    if password in blacklisted_passwords:
        return _('That password is too common. Please choose another.')
    return None


class PasswordEditForm(forms.ModelForm):
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))

    class Meta:
        model = UserProfile
        fields = ('password',)
        widgets = {
            'password': forms.PasswordInput(attrs={'render_value': 'False'}),
        }

    def clean_password(self):
        password = self.cleaned_data['password']
        message = check_password_complexity(password)
        if message:
            self._errors['password'] = forms.util.ErrorList([message])
        return password

    def clean(self):
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                self._errors['password_confirm'] = forms.util.ErrorList([
                    _('Passwords do not match.')])
        return data
