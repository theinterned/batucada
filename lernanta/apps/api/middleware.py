from django.http import HttpResponsePermanentRedirect
from django.conf import settings

class APISubdomainMiddleware:
    def process_request(self, request):
        """Parse out the subdomain from the request and redirect to API"""
        if settings.API_SERVER == None:
          return

        host = request.META.get('HTTP_HOST', '')
        host_s = host.replace('www.', '').split('.')

        if request.is_secure():
          protocol = 'https://'
        else:
          protocol = 'http://'

        if ((host_s[0] == 'api') and request.path.startswith('/v')):
          return HttpResponsePermanentRedirect(protocol + settings.API_SERVER 
              + '/api' + request.path + '?' + request.GET.urlencode(safe='&'))
        return
