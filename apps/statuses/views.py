from django.http import HttpResponseRedirect

from statuses.models import Status

def show(request, status_id):
    return HttpResponse('wahey')

def create(request):
    if 'status' not in request.POST:
        return HttpResponseRedirect('/')
    status = Status(author=request.user,
        status=request.POST['status'])
    status.save()
    return HttpResponseRedirect('/')
