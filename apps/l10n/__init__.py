from django.core import urlresolvers as django_urlresolvers
from l10n import urlresolvers

django_urlresolvers.reverse = urlresolvers.reverse
