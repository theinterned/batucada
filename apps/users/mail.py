from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
    
def send_reset_email(user, token, uri_func, view='users_reset_password_form'):
    """Send instructions to user on how to reset their password."""
    path = reverse(view, kwargs={'username':user.username, 'token':token})
    uri = uri_func(path)
    user.email_user(
        _('Password Reset'),
        _('Use the following link:\n%(uri)s' % {'uri':uri})
    )

def send_registration_email(user, token, uri_func, view='users_confirm_registration'):
    """Send instructions for completing registration."""
    path = reverse(view, kwargs={'username':user.username, 'token':token})
    uri = uri_func(path)
    user.email_user(
        _('Complete Registration'),
        _('Visit the following link:\n%(uri)s' % {'uri':uri})
    )
    
