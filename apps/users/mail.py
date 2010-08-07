from django.utils.translation import ugettext as _

from l10n.urlresolvers import reverse

def send_reset_email(user, token, uri_func, view='users.views.reset_password_form'):
    """Send instructions to user on how to reset their password."""
    path = reverse(view, kwargs={'username':user.username, 'token':token})
    uri = uri_func(path)
    user.email_user(
        _('Password Reset'),
        _('Use the following link:\n%(uri)s' % {'uri':uri})
    )
