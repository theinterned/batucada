from django.conf import settings
from django.utils.translation import activate, get_language
from django.template.loader import render_to_string


def localize_email(subject_template, body_template, context):
    current_locale = get_language()
    subjects = {}
    bodies = {}
    for locale, name in settings.SUPPORTED_LANGUAGES:
        activate(locale)
        subjects[locale] = render_to_string(subject_template, context).strip()
        bodies[locale] = render_to_string(body_template, context).strip()
    activate(current_locale)
    return subjects, bodies
