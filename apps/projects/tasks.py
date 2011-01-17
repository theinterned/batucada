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

    def create_frames(self, media):
        """
        Using ffmpeg, extract one image per frame for the first n frames
        of a video file, where n is specified by the ``FFMPEG_VFRAMES``
        configuration variable.
        """
        working_dir = getattr(settings, 'FFMPEG_WD', '/tmp')
        abs_path = os.path.join(settings.MEDIA_ROOT, media.project_file.name)
        framemask = self.frame_prefix + ".%d.jpg"
        cmd = '%s -y -an -vframes %d -r 1 -i %s %s -v 1 > /dev/null 2>&1' % (
            self.ffmpeg, self.vframes, abs_path, framemask)
        os.chdir(working_dir)
        return_value = os.system(cmd)
        log.debug("Running command: %s" % (cmd,))
        if return_value != 0:
            log.warn("ffmpeg returned non-zero: %d" % (return_value,))
            return False
        return True

    def create_thumbnail(self, media):
        """
        Select a random frame from the video to use as the video thumbnail.
        """
        image = "%s.%d.jpg" % (self.frame_prefix,
                               random.choice(range(1, self.vframes + 1)),)
        if not os.path.exists(image):
            log.warn("File %s does not exist!" % (image,))
            return
        thumbnail, ext = os.path.splitext(os.path.basename(image))
        thumbnail_filename = self.determine_path(
            media.project, "%s_thumbnail.png" % (thumbnail,))
        media.thumbnail = thumbnail_filename
        media.save()
        abs_path = os.path.join(settings.MEDIA_ROOT, thumbnail_filename)
        im = Image.open(image)
        im.thumbnail((128, 128), Image.ANTIALIAS)
        im.save(abs_path, 'PNG')
        return True

    def run(self, media):

        self.ffmpeg = getattr(settings, 'FFMPEG_PATH', None)
        self.vframes = getattr(settings, 'FFMPEG_VFRAMES', 10)

        if not self.ffmpeg:
            log.warn("No ffmpeg path set. Nothing to do.")
            return

        self.frame_prefix = "frame%d_%d" % (media.project.id, media.id)

        if not self.create_frames(media):
            log.warn("Error creating frames.")
            return

        if not self.create_thumbnail(media):
            log.warn("Error creating thumbnail")
            return

        # remove frame image files.
        files = glob.glob(self.frame_prefix + '*')
        for f in files:
            os.unlink(f)
