from django.contrib import messages as django_messages
from django.template.loader import render_to_string

# Idea taken from Zamboni. Wrap functions in the Django messages contrib
# application so we can mark certain messages safe and insert HTML.


def _make_message(message, safe=False):
    c = {'message': message, 'safe': safe}
    return render_to_string('drumbeat/message_content.html', c)


def info(request, message, extra_tags='', fail_silently=False, safe=False):
    msg = _make_message(message, safe)
    django_messages.info(request, msg, extra_tags, fail_silently)


def debug(request, message, extra_tags='', fail_silently=False, safe=False):
    msg = _make_message(message, safe)
    django_messages.debug(request, msg, extra_tags, fail_silently)


def success(request, message, extra_tags='', fail_silently=False, safe=False):
    msg = _make_message(message, safe)
    django_messages.success(request, msg, extra_tags, fail_silently)


def warning(request, message, extra_tags='', fail_silently=False, safe=False):
    msg = _make_message(message, safe)
    django_messages.warning(request, msg, extra_tags, fail_silently)


def error(request, message, extra_tags='', fail_silently=False, safe=False):
    msg = _make_message(message, safe)
    django_messages.error(request, msg, extra_tags, fail_silently)
