from django.conf import settings


def django_conf(request):
    return {
        'settings': settings,
        'query_string': request.GET.urlencode(),
        'request': request,
    }
