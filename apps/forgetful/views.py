from django.contrib.auth.models import User
from django.http import HttpResponseRedirect

import jingo

from l10n.urlresolvers import reverse
from users.decorators import anonymous_only
from forgetful.forms import ForgotPasswordForm
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

                # store new token
                token = User.objects.make_random_password(length=32)
                PasswordResetToken(user=user, token=token).save()

                # send email to user with URI for resetting password
                path = reverse('forgetful.views.reset',
                               kwargs=dict(token=token, username=user.username))
                uri = request.build_absolute_uri(path)
                user.email_user(_('Password Reset'),
                                _('Visit the following URL:\n%(uri)s' %
                                  dict(uri=uri)))
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

    try:
        user = User.objects.get(username__exact=username)
        token_obj = PasswordResetToken.objects.get(user__exact=user.id)
        if not token_obj.check_token(token):
            raise
    except:
        error = _('Invalid token or username.')

    if request.method == 'POST':
        form = PasswordResetForm(data=request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(username__exact=username)
                token_obj = PasswordResetToken.objects.get(user__exact=user.id)
                if token_obj.check_token(token):
                    user.set_password(form.cleaned_data['password'])
                    user.save()
                    token_obj.delete()
                    return HttpResponseRedirect('/')
                else:
                    error = _('Invalid Token.')
            except:
                error = _('Sorry, username and token do not match.')
                
    return jingo.render(request, 'forgetful/reset_password.html', {
        'username': username,
        'token': token,
        'form': form,
        'error': error
    })
