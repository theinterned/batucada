from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
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
    
    if 'object_id' not in request.POST or 'object_type_id' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")

    obj_type = ContentType.objects.get(id=int(request.POST['object_type_id']))
    target = obj_type.get_object_for_this_type(id=int(request.POST['object_id']))
    rel = Relationship(source=request.user, target=target)
    rel.save()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])

@login_required
@require_http_methods(['POST'])
def unfollow(request):

    if 'object_id' not in request.POST or 'object_type_id' not in request.POST:
        # todo - report error usefully
        return HttpResponse("error")
    
    obj_type = ContentType.objects.get(id=int(request.POST['object_type_id']))
    target = obj_type.get_object_for_this_type(id=int(request.POST['object_id']))

    rel = Relationship.objects.get(
        source_object_id__exact=request.user.id,
        target_object_id__exact=target.pk,
        target_content_type__exact=obj_type)
    rel.delete()

    return HttpResponseRedirect(request.META['HTTP_REFERER'])
