from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

class RegisterForm(forms.Form):
    username = forms.RegexField(
        regex=r'^\w+$', max_length=30,
        error_messages={'required': _('Username is required.')})
    password = forms.CharField(
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': _('Password is required.')})
    password_confirm = forms.CharField(
        label=_('Password (Again)'),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': _('Please confirm your password.')})
    email = forms.EmailField(
        label=_('Email Address'),
        error_messages={'required': _('Email Address is required.')})

    def clean_username(self):
        """Verify that the username doesn't already exist."""
        username = self.cleaned_data['username']
        user = User.objects.filter(username__exact=username)
        errormsg = _('Username already taken. Please choose another.')
        if len(user):
            raise forms.ValidationError(errormsg)
        return username

    def clean_email(self):
        """Verify that the email address isn't taken already."""
        email = self.cleaned_data['email']
        user = User.objects.filter(email__exact=email)
        errormsg = _('Email address already used. Please choose another.')
        if len(user):
            raise forms.ValidationError(errormsg)
        return email

    def clean(self):
        """Ensure password and password_confirm match."""
        data = self.cleaned_data
        if 'password' in data and 'password_confirm' in data:
            if data['password'] != data['password_confirm']:
                raise forms.ValidationError(_('Passwords do not match.'))
        return data

    def save(self):
        """Create user account."""
        if self.is_valid():
            user = User(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email']
            )
            user.set_password(self.cleaned_data['password'])
            user.save()
            return user
        else:
            raise forms.ValidationError("Cannot save user")

class OpenIDRegisterForm(forms.Form):
    openid_identifier = forms.URLField(required=True)

    def clean_openid_identifier(self):
        """Verify that the openid identifier isn't taken already."""
        return self.cleaned_data['openid_identifier']

    def save(self):
        """Create user account and associate it to the OpenID identifier."""
        pass
