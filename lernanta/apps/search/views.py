from django.shortcuts import render_to_response
from django.template import RequestContext


def search(request):
    return render_to_response('search/search.html',
        {}, context_instance=RequestContext(request))
