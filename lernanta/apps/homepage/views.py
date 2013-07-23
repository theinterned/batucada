# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext


def home(request):
    context = {}

    return render_to_response('homepage/home.html', context, context_instance=RequestContext(request))
