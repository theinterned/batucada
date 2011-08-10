from django import template


register = template.Library()


def pagination_links(context):
    request = context['request']
    page_url = context['page_url']
    prefix = context['prefix']
    current_page = context[prefix + 'pagination_current_page']
    page_number = context[prefix + 'pagination_current_page_number']

    page_number_param = prefix + 'pagination_page_number'
    prev_page_url = next_page_url = None
    if current_page.has_previous():
        prev_get_params = request.GET.copy()
        if page_number_param in prev_get_params:
            del prev_get_params[page_number_param]
        prev_get_params[page_number_param] = page_number - 1
        prev_page_url = page_url + '?%s' % prev_get_params.urlencode()
    if current_page.has_next():
        next_get_params = request.GET.copy()
        if page_number_param in next_get_params:
            del next_get_params[page_number_param]
        next_get_params[page_number_param] = page_number + 1
        next_page_url = page_url + '?%s' % next_get_params.urlencode()

    return {
        'prev_page_url': prev_page_url,
        'next_page_url': next_page_url,
    }

register.inclusion_tag('pagination/pagination_links.html', takes_context=True)(pagination_links)
