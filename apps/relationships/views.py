from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.views.decorators.http import require_http_methods

import jingo

from l10n.urlresolvers import reverse
from relationships.models import UserRelationship

@login_required
def following(request):
    following = UserRelationship.get_relationships_from(request.user)
    users = [User.objects.get(id=user) for user in following]
    return jingo.render(request, 'users/user_list.html', {
        'heading' : _('Users you follow'),
        'users' : users,
        'following' : following
    })

@login_required
def followers(request):
    followers = UserRelationship.get_relationships_to(request.user)
    users = [User.objects.get(id=user) for user in followers]
    return jingo.render(request, 'users/user_list.html', {
        'heading' : _('Users following you'),
        'users' : users,
        'following' : followers
    })

@login_required
@require_http_methods(['POST'])
def follow(request):
    if 'user' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")
    user = User.objects.get(id=int(request.POST['user']))
    rel = UserRelationship(from_user=request.user, to_user=user)
    rel.save()
    # todo - redirect user to whatever page they were on before.
    return HttpResponseRedirect(reverse('users.views.user_list'))

@login_required
@require_http_methods(['POST'])
def unfollow(request):
    if 'user' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")
    user = User.objects.get(id=int(request.POST['user']))
    rel = UserRelationship.objects.get(
        from_user__exact=request.user.id,
        to_user__exact=user.id)
    rel.delete()
    # todo - redirect user to whatever page they were on before.
    return HttpResponseRedirect(reverse('users.views.user_list'))
