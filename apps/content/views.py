from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from users.decorators import login_required
from drumbeat import messages

from content.forms import PageForm, NotListedPageForm
from content.models import Page

def show_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render_to_response('content/page.html', {
        'page': page,
    }, context_instance=RequestContext(request))


@login_required
def edit_page(request, slug):
    page = get_object_or_404(Page, slug=slug)
    user = request.user.get_profile()
    if page.project.created_by != user:
        raise Http404
    if page.listed:
        form_cls = PageForm
    else:
        form_cls = NotListedPageForm
    if request.method == 'POST':
        form = form_cls(request.POST, instance=page)
        if form.is_valid():
            form.save()
            messages.success(request, _('Page updated!'))
            return HttpResponseRedirect(reverse('page_show', kwargs={
                'slug': page.slug,
            }))
        else:
            messages.error(request,
                           _('There was a problem saving the page.'))
    else:
        form = form_cls(instance=page)
    return render_to_response('content/edit_page.html', {
        'form': form,
        'page': page,
    }, context_instance=RequestContext(request))

