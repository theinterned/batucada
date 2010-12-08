from django.contrib.auth.models import User, UserManager
from messages.models import Message, MessageManager

from activity.models import Activity, ActivityManager
from activity.models import Actor, ActorManager

import caching.base


for cls in (Message, User, Activity, Actor):
    cls.__bases__ += (caching.base.CachingMixin,)

for cls in (MessageManager, UserManager, ActivityManager, ActorManager):
    cls.__bases__ = (caching.base.CachingManager,) + cls.__bases__
