from django import template

register = template.Library()

@register.simple_tag
def tag_string(filter_tags, tag):
    filter_list = []
    filter_list += filter_tags
    filter_list += [tag]
    return '+'.join(filter_list)
