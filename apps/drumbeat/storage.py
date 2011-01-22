import os
import Image

from django.core.files.storage import FileSystemStorage


class ImageStorage(FileSystemStorage):

    format_extensions = {
        'PNG': 'png',
        'GIF': 'gif',
        'JPEG': 'jpg',
        'JPG': 'jpg',
    }

    def _save(self, name, content):
        name, ext = os.path.splitext(name)
        image = Image.open(content)
        image.save(content, image.format)
        if image.format in self.format_extensions:
            name = "%s.%s" % (name, self.format_extensions[image.format])
        return super(ImageStorage, self)._save(name, content)
