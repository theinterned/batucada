from django import http
from django.views.decorators.csrf import csrf_exempt

from notifications.models import post_notification_response

import logging
log = logging.getLogger(__name__)

@csrf_exempt
def response(request):
    """ Web hook called when a response to a notification is received """

    log.debug("notifications.views.response")

    if not request.method == 'POST':
        raise http.Http404

    to_email = request.POST.get('to')
    from_email = request.POST.get('from')
    reply_text = request.POST.get('text')

    # clean up reply_text - original notification text should be removed by
    # module that sent the notification
    reply_text = reply_text.strip()
    if reply_text.startswith("['"):
        reply_text = reply_text[2:]
    if reply_text.endswith("']'"):
        reply_text = reply_text[:-2]
    
    # get response token from 'reply+token@reply.p2pu.org'
    token_text = None
    if to_email.find('+') != -1 and to_email.find('@') != -1:
        token_text = to_email[to_email.index('+')+1:to_email.index('@')]

    # convert 'User Name <email@server.com>' to 'email@server.com'
    if from_email.find('<') != -1 and from_email.find('>') != -1:
        from_email = from_email[from_email.index('<')+1:from_email.index('>')]

    if token_text and from_email and reply_text:
        post_notification_response(token_text, from_email, reply_text)
    else:
        log.error("notifications.response: Invalid response")

    return http.HttpResponse(status=200)
