from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import forms as auth_forms
from django.utils.translation import ugettext as _

from captcha import fields as captcha_fields

from users.models import UserProfile

from drumbeat.utils import slug_validator


class AuthenticationForm(auth_forms.AuthenticationForm):
    remember_me = forms.BooleanField(required=False)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    password_confirm = forms.CharField(
        max_length=255,
        widget=forms.PasswordInput(render_value=False))
    recaptcha = captcha_fields.ReCaptchaField()

    class Meta:
        model = UserProfile

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)

        if not settings.RECAPTCHA_PRIVATE_KEY:
            del self.fields['recaptcha']

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


class SetPasswordForm(auth_forms.SetPasswordForm):

    def __init__(self, *args, **kwargs):
        super(SetPasswordForm, self).__init__(*args, **kwargs)

        # make sure to set the password in the user profile
        if isinstance(self.user, User):
            self.user = self.user.get_profile()
