try:
    import json
except ImportError:
    import simplejson as json

from django.http import HttpResponse

def handle(request):
    amcd = {
        'methods': {
        }
    }
    response = HttpResponse(json.dumps(amcd, sort_keys=True, indent=4))
    response['Content-type'] = 'application/json'
    return response
