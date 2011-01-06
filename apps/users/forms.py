import re

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext as _

from captcha import fields as captcha_fields

from users.blacklist import passwords as blacklisted_passwords
from users.models import UserProfile
from links.models import Link
from drumbeat.utils import slug_validator


class AuthenticationForm(auth_forms.AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'tabindex': '1'}))
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(attrs={'tabindex': '2'},
                                   render_value=False))
    remember_me = forms.BooleanField(required=False,
                                     widget=forms.CheckboxInput(
                                         attrs={'tabindex': '3'}))


def check_password_complexity(password):
    message = _('Password must be at least 8 ' +
                'characters long and contain ' +
                'both numbers and letters')
    if len(password) < 8 or not (
        re.search('[A-Za-z]', password) and re.search('[0-9]', password)):
        return message
    if password in blacklisted_passwords:
        return _('That password is too common. Please choose another.')
    return None


class SetPasswordForm(auth_forms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        # make sure to set the password in the user profile
        if isinstance(self.user, User):
            self.user = self.user.get_profile()

    def clean_new_password1(self):
        password = self.cleaned_data['new_password1']
        message = check_password_complexity(password)
        if message:
            self._errors['new_password1'] = forms.util.ErrorList([message])
        return password


class OpenIDForm(forms.Form):
    openid_identifier = forms.URLField(
        widget=forms.TextInput(attrs={
            'placeholder': _('enter your own OpenID URL')}))


class CreateProfileForm(forms.ModelForm):
    recaptcha = captcha_fields.ReCaptchaField()
    policy_optin = forms.BooleanField(required=True, error_messages={
        'required': _('You must agree to the licensing terms.')})

    class Meta:
        model = UserProfile
        fields = ('username', 'display_name',
                  'bio', 'image', 'newsletter', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
        }


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    recaptcha = captcha_fields.ReCaptchaField()
    policy_optin = forms.BooleanField(required=True, error_messages={
        'required': _('You must agree to the licensing terms.')})

    class Meta:
        model = UserProfile
        widgets = {
            'username': forms.TextInput(attrs={'autocomplete': 'off'}),
        }

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        if not settings.RECAPTCHA_PRIVATE_KEY:
            del self.fields['recaptcha']

    def clean_username(self):
        """Make sure that username has no invalid characters."""
        username = self.cleaned_data['username']
        slug_validator(username, lower=False)
        return username

    def clean_password(self):
        password = self.cleaned_data['password']
        message = check_password_complexity(password)
        if message:
            self._errors['password'] = forms.util.ErrorList([message])
        return password

    def clean(self):
        """Ensure password and password_confirm match."""
        super(RegisterForm, self).clean()
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                self._errors['password_confirm'] = forms.util.ErrorList([
                    _('Passwords do not match.')])
        return data


class ProfileEditForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('confirmation_code', 'password', 'username', 'email',
                   'created_on', 'user', 'image', 'featured')


class ProfileImageForm(forms.ModelForm):

    class Meta:
        model = UserProfile
        exclude = ('confirmation_code', 'password', 'username',
                   'email', 'created_on', 'user', 'featured')

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            raise forms.ValidationError(
                _("Image exceeds max image size: %(max)dk",
                  dict(max=max_size)))
        return self.cleaned_data['image']


class ProfileLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        exclude = ('project', 'user', 'subscription')
