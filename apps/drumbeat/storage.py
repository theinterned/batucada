import os
import Image

from django.core.files.storage import FileSystemStorage


class ImageStorage(FileSystemStorage):
    def _save(self, name, content):
        name, ext = os.path.splitext(name)
        image = Image.open(content)
        image.save(content, image.format)
        format_extensions = {
            'PNG': 'png',
            'GIF': 'gif',
            'JPEG': 'jpg',
        }
        if image.format in format_extensions:
            name = "%s.%s" % (name, format_extensions[image.format])
        return super(ImageStorage, self)._save(name, content)
