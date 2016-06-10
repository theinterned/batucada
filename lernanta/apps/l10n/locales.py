# -*- coding: utf-8 -*-
# l10n support. Mostly taken from kitsune and zamboni.
#
# http://github.com/mozilla/kitsune
# http://github.com/mozilla/zamboni

from collections import namedtuple

import json
import os

Language = namedtuple(u'Language',
                      u'external internal english native dictionary')

file = os.path.join(os.path.dirname(__file__), 'languages.json')
locales = json.loads(open(file, 'r').read())

LOCALES = {}

for k in locales:
    LOCALES[k] = Language(locales[k]['external'], locales[k]['internal'],
                          locales[k]['English'], locales[k]['native'],
                          locales[k]['dictionary'])

INTERNAL_MAP = dict([(LOCALES[k].internal, k) for k in LOCALES])
LANGUAGES = dict([(i.lower(), LOCALES[i].native) for i in LOCALES])
LANGUAGE_URL_MAP = dict([(i.lower(), i) for i in LOCALES])
