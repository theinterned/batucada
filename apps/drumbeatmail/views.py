import datetime
import operator

from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from drumbeat import messages
from drumbeatmail import forms
from messages.models import Message
from users.models import UserProfile


def _get_sorted_senders(user):
    msgs = Message.objects.inbox_for(user)
    senders = {}
    for msg in msgs:
        sender = msg.sender.get_profile()
        senders.setdefault(sender, 0)
        senders[sender] += 1
    return sorted(senders.iteritems(), key=operator.itemgetter(1))


@login_required
def inbox(request):
    inbox = Message.objects.inbox_for(request.user)[:10]
    senders = _get_sorted_senders(request.user)
    for msg in inbox:
        msg.read_at = datetime.datetime.now()
        msg.save()
    return render_to_response('drumbeatmail/inbox.html', {
        'inbox': inbox,
        'senders': senders,
    }, context_instance=RequestContext(request))


@login_required
def inbox_filtered(request, filter):
    sender = get_object_or_404(UserProfile, username=filter)
    inbox = Message.objects.inbox_for(request.user).filter(
        sender=sender)
    senders = _get_sorted_senders(request.user)
    return render_to_response('drumbeatmail/inbox.html', {
        'inbox': inbox,
        'senders': senders,
    }, context_instance=RequestContext(request))


@login_required
def outbox(request):
    outbox = Message.objects.outbox_for(request.user)
    senders = _get_sorted_senders(request.user)
    return render_to_response('drumbeatmail/inbox.html', {
        'inbox': outbox,
        'senders': senders,
    }, context_instance=RequestContext(request))


@login_required
def reply(request, message):
    message = get_object_or_404(Message, id=message)
    if message.recipient != request.user:
        return HttpResponseForbidden()
    if request.method == 'POST':
        form = forms.ComposeForm(data=request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.success(request, _('Message successfully sent.'))
            return HttpResponseRedirect(reverse('drumbeatmail_inbox'))
        else:
            messages.error(request, _('There was an error sending your message'
                                      '. Please try again.'))
    else:
        form = forms.ComposeForm(initial={
            'recipient': message.sender.get_profile().username,
            'subject': 'Re: %s' % (message.subject,),
        })
    return render_to_response('drumbeatmail/reply.html', {
        'form': form,
        'message': message,
    }, context_instance=RequestContext(request))


@login_required
def compose(request):
    if request.method == 'POST':
        form = forms.ComposeForm(data=request.POST)
        if form.is_valid():
            form.save(sender=request.user)
            messages.success(request, _('Message successfully sent.'))
            return HttpResponseRedirect(reverse('drumbeatmail_inbox'))
        else:
            messages.error(request, _('There was an error sending your message'
                                      '. Please try again.'))
    else:
        form = forms.ComposeForm()
    return render_to_response('drumbeatmail/compose.html', {
        'form': form,
    }, context_instance=RequestContext(request))
