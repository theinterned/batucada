"""
Based on the filters at:
* http://djangosnippets.org/snippets/858/
* https://gist.github.com/422828
"""

import re

from django.template.defaultfilters import stringfilter
from django import template


register = template.Library()

YOUTUBE_RE = r"\[youtube:http://www.youtube.com/watch\?v=(?P<id>[A-Za-z0-9\-=_]{11})(&.*)?\]"
YOUTUBE_EMBED = """
<embed src="http://www.youtube.com/v/%s" type="application/x-shockwave-flash" allowfullscreen="true" width="425" height="344"></embed>
"""

def replace(match):
    return YOUTUBE_EMBED % match.group('id')

@register.filter
@stringfilter
def youtube(html):
    """Finds YouTube [youtube: ...] tags, and replace them with an embeddable
    HTML snippet.
    """
    return re.sub(YOUTUBE_RE, replace, html)

youtube.is_safe = True  # Don't escape HTML

