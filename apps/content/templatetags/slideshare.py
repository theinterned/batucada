import re

from django.template.defaultfilters import stringfilter
from django import template


register = template.Library()


SLIDESHARE_RE = r"\[slideshare:http://static.slidesharecdn.com/swf/(?P<url>.+\?doc=[A-Za-z0-9\-=_]+)(&.*)?\]"
SLIDESHARE_EMBED = """
<embed allowfullscreen="true" height="355" name="__sse7328741" src="http://static.slidesharecdn.com/swf/%s" type="application/x-shockwave-flash" width="425"></embed>
"""

def replace(match):
    return SLIDESHARE_EMBED % match.group('url')

@register.filter
@stringfilter
def slideshare(html):
    """Finds Slideshare [slideshare: ...] tags, and replace them with an embeddable
    HTML snippet.
    """
    return re.sub(SLIDESHARE_RE, replace, html)

slideshare.is_safe = True  # Don't escape HTML
