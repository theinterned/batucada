from django.db import models

import caching.base


class ModelBase(caching.base.CachingMixin, models.Model):
    objects = caching.base.CachingManager()

    class Meta:
        abstract = True
