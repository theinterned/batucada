import re
from datetime import datetime

from django.template.defaultfilters import stringfilter
from django import template
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from embedly import Embedly

from richtext.models import EmbeddedUrl


register = template.Library()


EMBED_RE = (r"\[(?:slideshare|youtube|embed):(?P<url>[^\]]+)]")
DEFAULT_EMBED = '<a href="%s">%s</a>'
url_validate = URLValidator(verify_exists=True)


def replace(match):
    url = match.group('url')
    try:
        url_validate(url)
        expiration_date = datetime.now() - settings.EMBEDLY_CACHE_EXPIRES
        embedded_urls = EmbeddedUrl.objects.filter(original_url=url,
            created_on__gte=expiration_date).order_by('-created_on')
        embedded_url = None
        if embedded_urls.exists():
            embedded_url = embedded_urls[0]
        else:
            embedly_key = getattr(settings, 'EMBEDLY_KEY', False)
            if embedly_key:
                client = Embedly(embedly_key)
                obj = client.oembed(url, maxwidth=460)
                embedded_url = EmbeddedUrl(original_url=obj.original_url,
                    html=(obj.html or ''), extra_data=obj.dict)
                embedded_url.save()
        if embedded_url and embedded_url.html:
            return embedded_url.html
    except ValidationError:
        return '[embed:Invalid Url]'
    return DEFAULT_EMBED % (url, url)


@register.filter
@stringfilter
def embed(html):
    """Finds Slideshare [slideshare: ...] tags, and replace them
    with an embeddable HTML snippet.
    """
    return '<div class="richtext_section">%s</div>' % re.sub(
        EMBED_RE, replace, html)

embed.is_safe = True  # Don't escape HTML
