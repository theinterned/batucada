import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django.template.loader import render_to_string

from pages.models import Page


import logging
log = logging.getLogger(__name__)


def show_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render_to_response('pages/page.html', {
        'page': page,
   }, context_instance=RequestContext(request))

