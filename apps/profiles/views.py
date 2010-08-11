from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods

import jingo

from l10n.urlresolvers import reverse

from profiles.forms import ImageForm, ProfileForm, ContactNumberForm
from profiles.models import Profile, ContactNumber

@login_required
def edit(request):
    """Create a new profile or edit an existing one."""
    form = ProfileForm()
    if request.method == 'POST':
        form = ProfileForm(data=request.POST)
        if form.is_valid():
            profile = request.user.get_profile()
            for key, value in form.cleaned_data.iteritems():
                setattr(profile, key, value)
            profile.save()
            return HttpResponseRedirect(reverse(
                'profiles.views.show',
                kwargs=dict(username=request.user.username)
            ))
    return jingo.render(request, 'profiles/edit.html', {
        'form': form,
        'profile': request.user.get_profile()
    })
    
@require_http_methods(['GET'])
def show(request, username):
    """Display profile for the specified user."""
    try:
        user = User.objects.get(username__exact=username)
    except User.DoesNotExist:
        raise Http404
    return jingo.render(request, 'profiles/public.html', {
        'user': user,
        'profile': user.get_profile()
    })

@login_required
def upload_image(request):
    """Upload profile image."""
    form = ImageForm()
    if request.method == 'POST':
        form = ImageForm(request.POST, request.FILES)
        if form.is_valid():
            profile = request.user.get_profile()
            profile.image = form.cleaned_data['image']
            profile.save()
            return HttpResponseRedirect(reverse(
                'profiles.views.show',
                kwargs=dict(username=request.user.username)
            ))
    return jingo.render(request, 'profiles/upload_image.html', {
        'profile': request.user.get_profile(),
        'form': form
    })

@login_required
@require_http_methods(['POST'])
def delete_number(request):
    """Delete a contact number after verifying ownership."""
    try:
        number_id = int(request.POST.get('number', 0))
        number = ContactNumber.objects.get(id=number_id)
        if number.profile.user.id != request.user.id:
            return HttpResponse('Unauthorized', status=401)
        number.delete()
    except ValueError:
        return HttpResponse('Bad Request', status=400)
    
    return HttpResponseRedirect(reverse('profiles.views.contact_numbers'))

@login_required
def contact_numbers(request):
    """Add contact numbers to a user profile."""
    form = ContactNumberForm()
    if request.method == 'POST':
        form = ContactNumberForm(request.POST)
        if form.is_valid():
            number = ContactNumber(
                profile=request.user.get_profile(),
                number=form.cleaned_data['number'],
                label=form.cleaned_data['label']
            )
            number.save()
            return HttpResponseRedirect(reverse(
                'profiles.views.contact_numbers',
            ))
    return jingo.render(request, 'profiles/contact_numbers.html', {
        'form': form,
        'profile': request.user.get_profile()
    })

@login_required
def profile_links(request):
    """Not Implemented Yet."""
    return jingo.render(request, 'profiles/links.html', {

    })

@login_required
def skills(request):
    """Not Implemented Yet."""
    return jingo.render(request, 'profiles/skills.html', {

    })

@login_required
def interests(request):
    """Not implemented Yet."""
    return jingo.render(request, 'profiles/interests.html', {
    })
