from django.db import models
from django.utils.translation import ugettext as _

from taggit.models import TagBase, GenericTaggedItemBase, ItemBase

class GeneralTag(TagBase):
    class Meta:
        verbose_name = _("Tag")
        verbose_name_plural = _("Tags")

class GeneralTaggedItem(GenericTaggedItemBase, ItemBase):

    tag = models.ForeignKey(GeneralTag, related_name="%(app_label)s_%(class)s_items")

    class Meta:
        verbose_name = _("Tagged Item")
        verbose_name_plural = _("Tagged Items")

    @classmethod
    def tags_ford(cls, model, instance=None):
        if instance is not None:
            return cls.tag_model().objects.filter(**{
                '%s__content_object' % cls.tag_relname(): instance
            })
        return cls.tag_model().objects.filter(**{
            '%s__content_object__isnull' % cls.tag_relname(): False
        }).distinct()
