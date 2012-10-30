from django import template
from django.template.defaultfilters import stringfilter

import markdown
import bleach

register = template.Library()

@register.filter
@stringfilter
def convert_content( markdown_text ):
    html = markdown.markdown(markdown_text, ['tables'])
    html = bleach.linkify(html, target="_blank")
    return html

convert_content.is_safe = True
