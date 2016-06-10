from django import http
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

from notifications.models import send_notifications_i18n
from notifications.models import send_notifications
from notifications.models import post_notification_response
from notifications.db import ResponseToken
from users.models import UserProfile

import simplejson as json
import logging
log = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def response(request):
    """ Web hook called when a response to a notification is received """

    log.debug("notifications.views.response")

    to_email = request.POST.get('to')
    from_email = request.POST.get('from')
    reply_text = request.POST.get('text')

    # clean up reply_text - original notification text should be removed by
    # module that sent the notification
    if reply_text:
        reply_text = reply_text.strip()
        if reply_text.startswith("['"):
            reply_text = reply_text[2:]
        if reply_text.endswith("']'"):
            reply_text = reply_text[:-2]

    # get response token from 'reply+token@reply.p2pu.org'
    token_text = None
    if to_email.find('+') != -1 and to_email.find('@') != -1:
        token_text = to_email[to_email.index('+')+1:to_email.index('@')]

    token = None
    try:
        token = ResponseToken.objects.get(response_token=token_text)
    except ResponseToken.DoesNotExist:
        log.error("Response token {0} does not exist".format(token_text))

    # convert 'User Name <email@server.com>' to 'email@server.com'
    if from_email.find('<') != -1 and from_email.find('>') != -1:
        from_email = from_email[from_email.index('<')+1:from_email.index('>')]

    user = None
    try:
        user = UserProfile.objects.get(email=from_email)
    except UserProfile.DoesNotExist:
        log.error(
            "Invalid user for response. User: {0}, Token: {1}".format(
                from_email, token_text
            )
        )

    if token and user and reply_text:
        post_notification_response(token, user, reply_text)
    else:
        log.error("notifications.response: Invalid response")

    return http.HttpResponse(status=200)


@csrf_exempt
@require_POST
def notifications_create(request):
    """ API call for creating notifications

        Json data should look like:
        {
            api-key: '34jsd8s04kl24j50sdf809sdfj',
            user: 'username',
            subject: 'Notification subject',
            text: 'Notification text.\nProbably containing multiple paragraphs',
            html: '<html><head></head><body><p>Notification text.</p></body></html>',
            callback: 'https://mentors.p2pu.org/api/reply',
            sender: 'Bob Bader',
            category: 'badge-awarded.web-maker-badge'
        }

        Translation is the callers responsibility!
    """

    notification_json = json.loads(request.raw_post_data)

    api_key = notification_json.get('api-key')
    if not api_key == settings.INTERNAL_API_KEY:
        return http.HttpResponseForbidden()

    username = notification_json.get('user')
    subject = notification_json.get('subject')
    text = notification_json.get('text')
    html = notification_json.get('html')
    callback_url = notification_json.get('callback')
    sender = notification_json.get('sender')
    # TODO don't default to badge once other app use this API!
    notification_category = notification_json.get('category', 'badges')

    # find user
    user = None
    try:
        user = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        log.error("username {0} does not exist")

    if user and subject and text:
        send_notifications([user], subject, text, html, callback_url, sender,
            notification_category=notification_category
        )
        return http.HttpResponse(status=200)

    raise http.Http404
