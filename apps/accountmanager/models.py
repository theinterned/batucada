from django.conf import settings

import wellknown
from wellknown.resources import HostMeta
from xrd import Link

amcd_href = getattr(settings, 'MOZILLA_AMCD_HREF', '/meta/amcd.json')

# hack. At this point it's hard to tell if a host-meta handler has already
# been registered in the django-wellknown application, so clobber it here
# and add it again. In the case that it doesn't exist ``wellknown.get_hostmeta``
# will return ``None`` and we wouldn't be able to append a ``Link`` here. 
try:
    wellknown.register('host-meta', handler=HostMeta(),
                       content_type='application/xrd+xml')
    hostmeta = wellknown.get_hostmeta()
    hostmeta.links.append(Link(
        rel='http://services.mozilla.com/amcd/0.1', href=amcd_href))
except ValueError:
    pass
