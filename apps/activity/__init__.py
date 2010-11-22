import logging

from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from activity.models import Activity
from activity.schema import verbs, UnknownActivityError

log = logging.getLogger(__name__)


def send(actor, verb, obj, target=None, timestamp=None):
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
        verb=verb.name,
        obj_content_type=ContentType.objects.get_for_model(obj),
        obj_id=obj.pk,
    )
    if isinstance(actor, User):
        log.debug("Setting actor to %r" % (repr(actor),))
        activity.actor = actor
    else:
        log.debug("Setting actor string to %r" % (repr(actor),))
        activity.actor_string = actor
    if target:
        log.debug("Setting target to %r" % (repr(target),))
        content_type = ContentType.objects.get_for_model(target)
        activity.target_content_type = content_type
        activity.target_id = target.pk
    activity.save()
    if timestamp:
        log.debug("Setting timestamp to %r" % (repr(timestamp),))
        activity.timestamp = timestamp
        activity.save()
    return activity
