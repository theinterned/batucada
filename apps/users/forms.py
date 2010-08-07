from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from users.models import ConfirmationToken

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
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            user.save()
            return user
        else:
            raise forms.ValidationError("Cannot save user")

class LoginForm(forms.Form):
    username = forms.CharField(
        label=_("Username or Email:"),
        error_messages={'required': _('You must provide a username or email.')})
    password = forms.CharField(
        label=_("Password:"),
        widget=forms.PasswordInput(render_value=False),
        error_messages={'required': _('Password is required.')})

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
                user = User.objects.get(username__exact=data['username'])
            except User.DoesNotExist:
                raise forms.ValidationError(_('User does not exist.'))
            try:
                token = ConfirmationToken.objects.get(user__exact=user.id)
            except ConfirmationToken.DoesNotExist:
                raise forms.ValidationError(_('Token does not exist.'))

            if not token.check_token(data['token']):
                raise forms.ValidationError(_('Invalid token.'))
        
        return data
