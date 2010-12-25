from xml import sax
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


from BeautifulSoup import BeautifulSoup


class FeedHandler(sax.ContentHandler):
    """Parse RSS and Atom feeds and look for a PubSubHubbub hub."""
    href = None

    def startElementNS(self, name, qname, attrs):
        """Return href of link element with a rel attribute of 'hub'."""
        if name != ('http://www.w3.org/2005/Atom', 'link'):
            return
        # drop namespace from attr names, build a dictionary of
        # local attribute name = value.
        fixed = {}
        for name, value in attrs.items():
            (namespace, local) = name
            fixed[local] = value
        if not ('rel' in fixed and fixed['rel'] == 'hub'):
            return
        if not 'href' in fixed:
            return
        self.href = fixed['href']
        raise sax.SAXException('done')  # hacky way to signal that we're done.


def parse_feed_url(content):
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
            return hrefs[0]
    rss = get_by_type('application/rss+xml', alternates)
    if rss:
        hrefs = get_hrefs(rss)
        if hrefs:
            return hrefs[0]
    return None


def parse_hub_url(content):
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
    return handler.href or None
