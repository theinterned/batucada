import jingo

def index(request):
    if not request.user.is_authenticated():
        return jingo.render(request, 'dashboard/signin.html')
    return jingo.render(request, 'dashboard/dashboard.html', {
        'full_name' : request.user.get_full_name()
    })
