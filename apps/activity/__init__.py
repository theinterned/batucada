from django.contrib.contenttypes.models import ContentType

from activity.models import Activity
from activity.schema import verbs, UnknownActivityError

def send(actor, verb, obj, target=None):
    """
    Receive and handle an activity sent by another part of the project.
    Activities are represented as <actor> <verb> <object> [<target>]
    where actor is a ```User``` object, ```verb``` is a string and
    ```obj``` and optionally ```target``` are model classes.
    """
    if verb not in verbs:
        raise UnknownActivityError("Unknown verb: %s" % (verb,))
    verb = verbs[verb]
    activity = Activity(
        actor=actor,
        verb=verb.name,
        obj_content_type=ContentType.objects.get_for_model(obj),
        obj_id=obj.pk
    )
    if target:
        activity.target_content_type = ContentType.objects.get_for_model(target)
        activity.target_id = target.pk
    activity.save()
    return activity
