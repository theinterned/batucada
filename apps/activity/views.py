from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django import http
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.core.paginator import Paginator, EmptyPage

from l10n.urlresolvers import reverse
from users.decorators import login_required
from drumbeat import messages
from statuses.forms import StatusForm

from activity.models import Activity, FILTERS


def filter_activities(request, activities, default=None):
    if 'activities_filter' in request.GET:
        filter_name = request.GET['activities_filter']
        if filter_name in FILTERS:
            return FILTERS[filter_name](activities)
    if 'default' in FILTERS:
        return FILTERS['default'](activities)
    else:
        return activities


def index(request, activity_id, page=1):
    activity = get_object_or_404(Activity, id=activity_id)
    context = {
        'activity': activity,
        'domain': Site.objects.get_current().domain,
    }
    if activity.scope_object:
        scope_url = activity.scope_object.get_absolute_url()
        context['project'] = activity.scope_object
    else:
        scope_url = activity.actor.get_absolute_url()
        context['profile'] = activity.actor
        context['profile_view'] = True
    if activity.deleted:
        messages.error(request, _('This activity was deleted.'))
        if activity.can_edit(request.user):
            return http.HttpResponseRedirect(reverse('activity_restore',
                kwargs={'activity_id': activity.id}))
        return http.HttpResponseRedirect(scope_url)
    replies = activity.all_replies.filter(deleted=False).order_by(
        '-created_on')
    paginator = Paginator(replies, 25)
    try:
        current_page = paginator.page(page)
    except EmptyPage:
        raise http.Http404
    context.update({
        'paginator': paginator,
        'page_num': page,
        'next_page': int(page) + 1,
        'prev_page': int(page) - 1,
        'num_pages': paginator.num_pages,
        'page': current_page,
    })
    return render_to_response('activity/index.html', context,
        context_instance=RequestContext(request))


@login_required
def reply(request, activity_id):
    """Create a status update that is a reply to an activity."""
    reply_to = get_object_or_404(Activity, id=activity_id)
    if not reply_to.can_reply(request.user):
        messages.error(request, _("You can't reply to this activity"))
        return http.HttpResponseRedirect(reply_to.get_absolute_url())
    status = None
    if request.method == 'POST':
        form = StatusForm(data=request.POST)
        if form.is_valid():
            status = form.save(commit=False)
            status.author = request.user.get_profile()
            status.reply_to = reply_to
            status.project = reply_to.scope_object
            if 'show_preview' not in request.POST:
                status.save()
                return http.HttpResponseRedirect(status.get_absolute_url())
        else:
            messages.error(request, _('Please correct errors below.'))
    else:
        form = StatusForm()
    return render_to_response('activity/reply.html', {
        'reply_to': reply_to, 'preview': ('show_preview' in request.POST),
        'form': form, 'status': status,
    }, context_instance=RequestContext(request))


@login_required
def delete_restore(request, activity_id):
    activity = get_object_or_404(Activity, id=activity_id)
    if not activity.can_edit(request.user):
        return http.HttpResponseForbidden(_("You can't edit this activity"))
    if request.method == 'POST':
        activity.deleted = not activity.deleted
        activity.save()
        if activity.deleted:
            msg = _('Activity deleted!')
        else:
            msg = _('Activity restored!')
        messages.success(request, msg)
        if activity.scope_object:
            return http.HttpResponseRedirect(
                activity.scope_object.get_absolute_url())
        else:
            return http.HttpResponseRedirect(reverse('dashboard'))
    else:
        return render_to_response('activity/delete_restore.html', {
            'activity': activity,
        }, context_instance=RequestContext(request))
