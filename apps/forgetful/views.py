from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _

import jingo

from l10n.urlresolvers import reverse
from users.auth import authenticate
from users.decorators import anonymous_only
from forgetful.forms import ForgotPasswordForm, PasswordResetForm
from forgetful.models import PasswordResetToken

@anonymous_only
def forgot(request):
    """Prompt user for their email address so they can reset their password."""
    error = None
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(data=request.POST)
        if form.is_valid():
            try:
                email = form.cleaned_data['email']
                user = User.objects.get(email__exact=email)

                # delete existing reset token for user (if exists)
                PasswordResetToken.objects.filter(user__exact=user.id).delete()
                
                # create new token and send it to user
                token = User.objects.make_random_password(length=32)
                PasswordResetToken(user=user, token=token).save()
                path = reverse('forgetful.views.reset', kwargs=dict(
                    token=token,
                    username=user.username
                ))
                uri = request.build_absolute_uri(path)
                user.email_user(_('Password Reset'),
                                _('Use the following link:\n%(uri)s' % dict(
                                    uri=uri)))
                message = _("""An email has been sent to %(email)s with
                instructions for resetting your password.""" % {
                    'email': user.email})
                messages.add_message(request, messages.INFO, message)
                return HttpResponseRedirect(reverse('dashboard.views.index'))
            except User.DoesNotExist:
                error = _('Email address not found.')
    return jingo.render(request, 'forgetful/forgot_password.html', {
        'form'  : form,
        'error' : error
    })

@anonymous_only
def reset(request, token, username):
    """Allow user to reset their password."""
    error = None
    form = PasswordResetForm()
    invalid_data_message = _('Sorry, invalid username or token')

    try:
        user = User.objects.get(username__exact=username)
        token_obj = PasswordResetToken.objects.get(user__exact=user.id)
        if not token_obj.check_token(token):
            raise
    except:
        error = invalid_data_message

    if request.method == 'POST':
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username__exact=username)
                token_obj = PasswordResetToken.objects.get(user__exact=user.id)
                if token_obj.check_token(token):
                    password = form.cleaned_data['password']
                    user.set_password(password)
                    user.save()
                    token_obj.delete()
                    messages.add_message(
                        request, messages.INFO,
                        _('Your password has been reset!'))
                    user = authenticate(username=user.username, password=password)
                    if user is not None and user.is_active:
                        auth.login(request, user)
                    return HttpResponseRedirect('/')
                else:
                    error = invalid_data_message
            except:
                error = invalid_data_message
                
    return jingo.render(request, 'forgetful/reset_password.html', {
        'username': username,
        'token': token,
        'form': form,
        'error': error
    })
