from django import http
from django.core.paginator import Paginator, EmptyPage
from django.conf import settings


def get_pagination_context(request, objects, items_per_page=None, prefix=''):
    if not items_per_page:
        items_per_page = settings.PAGINATION_DEFAULT_ITEMS_PER_PAGE
    page_number = 1
    page_number_param = prefix + 'pagination_page_number'
    if page_number_param in request.GET:
        try:
            page_number = int(request.GET[page_number_param])
        except ValueError:
            pass
    paginator = Paginator(objects, items_per_page)
    try:
        current_page = paginator.page(page_number)
    except EmptyPage:
        raise http.Http404
    return {
        prefix + 'pagination_paginator': paginator,
        prefix + 'pagination_current_page': current_page,
        prefix + 'pagination_current_page_number': page_number,
        prefix + 'pagination_next_page_number': int(page_number) + 1,
        prefix + 'pagination_prev_page_number': int(page_number) - 1,
        prefix + 'pagination_pages_count': paginator.num_pages,
    }
