import re

from django.template import Library
from django.utils.encoding import force_unicode


register = Library()

r_nofollow = re.compile('<a (?![^>]*nofollow)')
s_nofollow = '<a rel="nofollow" '


def nofollow(value):
    return r_nofollow.sub(s_nofollow, force_unicode(value))

register.filter(nofollow)
