from django.db import models

import caching.base


class ManagerBase(caching.base.CachingManager, models.Manager):
    pass


class ModelBase(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    class Meta:
        abstract = True
