from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_http_methods

from relationships.models import Relationship


@login_required
@require_http_methods(['POST'])
def follow(request):
    """
    Create a relationship from the currently authenticated user and the
    object referred to by ``object_id`` and ``object_type_id`` in the
    POST parameters.
    """
    if 'object_id' not in request.POST or 'object_type_id' not in request.POST:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    obj_type = ContentType.objects.get(id=int(request.POST['object_type_id']))
    target = obj_type.get_object_for_this_type(
        id=int(request.POST['object_id']))
    rel = Relationship(source=request.user, target=target)
    rel.save()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])


@login_required
@require_http_methods(['POST'])
def unfollow(request):
    """
    Delete the relationship from the currently authenticated user and
    the object referred to by the ``object_id`` and ``object_type_id``
    POST parameters.
    """
    if 'object_id' not in request.POST or 'object_type_id' not in request.POST:
        return HttpResponseRedirect(request.META['HTTP_REFERER'])
    user_type = ContentType.objects.get_for_model(request.user)
    obj_type = ContentType.objects.get(id=int(request.POST['object_type_id']))
    target = obj_type.get_object_for_this_type(
        id=int(request.POST['object_id']))
    Relationship.objects.filter(
        source_object_id__exact=request.user.id,
        source_content_type__exact=user_type,
        target_object_id__exact=target.pk,
        target_content_type__exact=obj_type).delete()
    return HttpResponseRedirect(request.META['HTTP_REFERER'])
