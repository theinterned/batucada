from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _
from django import http

from users.decorators import login_required
from drumbeat import messages

from l10n.urlresolvers import reverse
from schools.decorators import organizer_required
from schools.models import School
from schools import forms as school_forms


def home(request, slug):
    school = get_object_or_404(School, slug=slug)
    user = request.user
    if user.is_authenticated():
        profile = user.get_profile()
        is_organizer = school.organizers.filter(id=profile.id).exists()
    else:
        is_organizer = False
    context = {
        'school': school,
        'is_organizer': is_organizer,
    }
    return render_to_response('schools/home.html', context,
                          context_instance=RequestContext(request))

@login_required
@organizer_required
def edit(request, slug):
    school = get_object_or_404(School, slug=slug)
    if request.method == 'POST':
        form = school_forms.SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, _('School updated!'))
            return http.HttpResponseRedirect(
                reverse('schools_edit', kwargs=dict(slug=school.slug)))
    else:
        form = school_forms.SchoolForm(instance=school)

    return render_to_response('schools/school_edit_summary.html', {
        'form': form,
        'school': school,
    }, context_instance=RequestContext(request))
