from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods
from django.shortcuts import render_to_response
from django.template import RequestContext
    
from relationships.models import Relationship

@login_required
def following(request):
    following = request.user.following()
    return render_to_response('users/user_list.html', {
        'heading' : _('Users you follow'),
        'users' : following,
        'following' : [user.id for user in following]
    }, context_instance=RequestContext(request))

@login_required
def followers(request):
    followers = request.user.followers()
    return render_to_response('users/user_list.html', {
        'heading' : _('Users following you'),
        'users' : followers,
        'following' : [user.id for user in request.user.following()]
    }, context_instance=RequestContext(request))

@login_required
@require_http_methods(['POST'])
def follow(request):
    if 'user' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")
    user = User.objects.get(id=int(request.POST['user']))
    rel = Relationship(source=request.user, target=user)
    rel.save()
    # todo - redirect user to whatever page they were on before.
    return HttpResponseRedirect(reverse('users_user_list'))

@login_required
@require_http_methods(['POST'])
def unfollow(request):
    if 'user' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")
    user = User.objects.get(id=int(request.POST['user']))
    rel = Relationship.objects.get(
        source_object_id__exact=request.user.id,
        target_object_id__exact=user.id)
    rel.delete()
    # todo - redirect user to whatever page they were on before.
    return HttpResponseRedirect(reverse('users_user_list'))
