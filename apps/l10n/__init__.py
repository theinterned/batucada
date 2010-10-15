from django.db import models

def permalink(func):
    """
    Decorator that calls l10n.urlresolvers.reverse() to return a URL using
    parameters returned by the decorated function "func".

    Note that this decorator is exactly the same as django.db.models.permalink
    except that it uses l10n.urlresolvers instead of django.core.urlresolvers.
    We monkey patch django.db.models here to make this behaviour the default.
    """
    from l10n.urlresolvers import reverse
    def inner(*args, **kwargs):
        bits = func(*args, **kwargs)
        return reverse(bits[0], None, *bits[1:3])
    return inner

models.permalink = permalink
