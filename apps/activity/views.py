from django.http import HttpResponse


def index(request, activity_id):
    return HttpResponse('activity_index')


def delete(request):
    return HttpResponse('activity_delete')
