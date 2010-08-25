from django.contrib.contenttypes.models import ContentType

from activity import normalize
from activity.models import Activity

def send(actor, verb, obj, target=None):
    activity = Activity(
        actor=actor,
        verb=normalize(verb),
        obj_content_type=ContentType.objects.get_for_model(obj),
        obj_id=obj.pk
    )
    if target:
        activity.target_content_type = ContentType.objects.get_for_model(target)
        activity.target_id = target.pk
    activity.save()
