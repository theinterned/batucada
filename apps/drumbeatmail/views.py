from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from drumbeat import messages
from drumbeatmail.forms import ComposeForm
from messages.models import Message


@login_required
def inbox(request):
    return render_to_response('drumbeatmail/inbox.html', {
        'inbox_messages': Message.objects.inbox_for(request.user),
    }, context_instance=RequestContext(request))


@login_required
def compose(request):
    if request.method == 'POST':
        form = ComposeForm(data=request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.success(request, _('Message successfully sent.'))
            return HttpResponseRedirect(reverse('drumbeatmail_inbox'))
        else:
            messages.error(request, _('Message not sent. Please try again.'))
    else:
        form = ComposeForm()
    return render_to_response('drumbeatmail/compose.html', {
        'form': form,
    }, context_instance=RequestContext(request))
