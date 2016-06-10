import urlparse

from xml import sax
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from BeautifulSoup import BeautifulSoup

from django.conf import settings


def normalize_url(url, base_url):
    """Try to detect relative URLs and convert them into absolute URLs."""
    parts = urlparse.urlparse(url)
    if parts.scheme and parts.netloc:
        return url  # looks fine
    if not base_url:
        return url
    base_parts = urlparse.urlparse(base_url)
    server = '://'.join((base_parts.scheme, base_parts.netloc))
    if server[-1] != '/' and url[0] != '/':
        server = server + '/'
    if server[-1] == '/' and url[0] == '/':
        server = server[:-1]
    return server + url


class FeedHandler(sax.ContentHandler):
    """Parse RSS and Atom feeds and look for a PubSubHubbub hub."""
    href = None

    def startElementNS(self, name, qname, attrs):
        """Return href of link element with a rel attribute of 'hub'."""

        # stop processing if we encounter entries or items.
        if name == ('', 'item'):
            raise sax.SAXException('encountered item element')
        if name == ('http://www.w3.org/2005/Atom', 'entry'):
            raise sax.SAXException('encountered entry element')

        # only elements we're concerned with now are links
        if name != ('http://www.w3.org/2005/Atom', 'link'):
            return

        # drop namespace from attr names, build a dictionary of
        # local attribute name = value.
        fixed = {}
        for name, value in attrs.items():
            (namespace, local) = name
            fixed[local] = value

        # only concerned with links with 'hub' rel and an href attr.
        if not ('rel' in fixed and fixed['rel'] == 'hub'):
            return
        if not 'href' in fixed:
            return

        self.href = fixed['href']
        raise sax.SAXException('done')  # hacky way to signal that we're done.


def parse_feed_url(content, url=None):
    """
    Parse the provided html and return the first Atom or RSS feed we find.
    Note that a preference is given to Atom if the HTML contains links to
    both.
    """
    soup = BeautifulSoup(content)
    links = soup.findAll('link')

    # BeautifulSoup instances are not actually dictionaries, so
    # we can't use the more proper 'key in dict' syntax and
    # must instead use the deprecated 'has_key()' method.
    alternates = [link for link in links
                  if link.has_key('rel') and link['rel'] == 'alternate']
    get_by_type = lambda t, links: [l for l in links
                           if l.has_key('type') and l['type'] == t]
    get_hrefs = lambda links: [l['href'] for l in links if l.has_key('href')]
    atom = get_by_type('application/atom+xml', alternates)
    if atom:
        hrefs = get_hrefs(atom)
        if hrefs:
            return normalize_url(hrefs[0], url)
    rss = get_by_type('application/rss+xml', alternates)
    if rss:
        hrefs = get_hrefs(rss)
        if hrefs:
            return normalize_url(hrefs[0], url)
    return None


def parse_hub_url(content, base_url=None):
    """Parse the provided xml and find a hub link."""
    handler = FeedHandler()
    parser = sax.make_parser()
    parser.setContentHandler(handler)
    parser.setFeature(sax.handler.feature_namespaces, 1)
    inpsrc = sax.xmlreader.InputSource()
    inpsrc.setByteStream(StringIO(content))
    try:
        parser.parse(inpsrc)
    except sax.SAXException:
        pass
    if handler.href is None:
        return handler.href
    return normalize_url(handler.href, base_url)


def hub_credentials(hub_url):
    """Credentials callback for django_push.subscribers"""
    if hub_url == settings.SUPERFEEDR_URL:
        return (settings.SUPERFEEDR_USERNAME, settings.SUPERFEEDR_PASSWORD)
    return None
