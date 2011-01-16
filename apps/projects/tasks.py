import os
import time
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

    def run(self, media):
        filename = os.path.join(settings.MEDIA_ROOT, media.project_file.name)
        ffmpeg = getattr(settings, 'FFMPEG_PATH', None)
        if not ffmpeg:
            log.warn("No ffmpeg path set, nothing to do.")
            return
        framemask = "frame" + str(time.time()) + ".%d.jpg"
        cmd = '%s -y -an -vframes 10 -r 1 -i %s %s -v 1 > /dev/null 2>&1' % (
            ffmpeg, filename, framemask)
        log.debug("Command: %s" % (cmd,))
        os.chdir("/tmp")
        ret = os.system(cmd)
        if ret != 0:
            log.warn("ffmpeg returned non-zero: %d" % (ret,))
            return
        image = framemask % (random.choice(range(1, 10)),)
        if not os.path.exists(image):
            log.warn("File %s does not exist!" % (image,))
            return
        thumbnail, ext = os.path.splitext(os.path.basename(filename))
        thumbnail_filename = self.determine_path(
            media.project, "%s_thumbnail.png" % (thumbnail,))
        media.thumbnail = thumbnail_filename
        media.save()
        abs_thumbnail = os.path.join(settings.MEDIA_ROOT, thumbnail_filename)
        log.debug("Abs path: %s" % (abs_thumbnail,))
        im = Image.open(image)
        im.thumbnail((128, 128), Image.ANTIALIAS)
        im.save(abs_thumbnail, 'PNG')
        #im.save(thumbnail_filename, "PNG")
