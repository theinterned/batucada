import os
import glob
import logging
import random

import Image

from django.conf import settings

from celery.task import Task

from drumbeat.utils import get_partition_id

log = logging.getLogger(__name__)


class ThumbnailGenerator(Task):

    def determine_path(self, project, filename):
        return "images/projects/%(partition)d/%(filename)s" % {
            'partition': get_partition_id(project.pk),
            'filename': filename,
        }

    def create_image_thumbnail(self, media):
        """Create a thumbnail for an image using PIL."""
        image = os.path.join(settings.MEDIA_ROOT, media.project_file.name)
        thumbnail_filename = self.determine_path(
            media.project, "%s_thumbnail.%s" % (os.path.splitext(
                os.path.basename(media.project_file.name))))
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, thumbnail_filename)
        im = Image.open(image)
        im.thumbnail((128, 128), Image.ANTIALIAS)
        im.save(thumbnail_path, im.format)
        media.thumbnail = thumbnail_filename
        media.save()
        return True

    def run(self, media):
        return self.create_image_thumbnail(media)

