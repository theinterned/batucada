from django import template

register = template.Library()

@register.simple_tag
def filter_add_tag(filter_tags, tag):
    filter_list = []
    filter_list += filter_tags
    filter_list += [tag]
    return '+'.join(filter_list)


@register.simple_tag
def filter_remove_tag(filter_tags, tag):
    filter_list = []
    filter_list += filter_tags
    try:
        filter_list.remove(tag)
    except:
        pass
    return '+'.join(filter_list)
