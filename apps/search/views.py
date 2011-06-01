from django.shortcuts import render_to_response
from django.template import RequestContext


def search(request):
    context = {}
    if 'q' in request.GET:
        context['q'] = request.GET['q']
    return render_to_response('search/search.html',
        context, context_instance=RequestContext(request))
