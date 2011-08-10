from django.conf import settings


def django_conf(request):
    return {
        'settings': settings,
        'request': request,
    }
