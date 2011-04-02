from django.conf import settings
from django import http
from django.template import RequestContext, Context, loader
from django.shortcuts import render_to_response
from django.contrib.contenttypes.models import ContentType

from users.models import UserProfile
from users.tasks import SendUserEmail
from drumbeat.forms import AbuseForm


def server_error(request):
    """Make MEDIA_URL available to the 500 template."""
    t = loader.get_template('500.html')
    return http.HttpResponseServerError(t.render(Context({
        'MEDIA_URL': settings.MEDIA_URL,
    })))


def report_abuse(request, content_type, pk):
    """Report abusive or irrelavent content."""
    if request.method == 'POST':
        # we only use the form for the csrf middleware. skip validation.
        form = AbuseForm(request.POST)
        content_type_cls = ContentType.objects.get(model=content_type).model_class()
        instance = content_type_cls.objects.get(pk=pk)
        url = request.build_absolute_uri(instance.get_absolute_url())
        body = """
        User %s has reported the following content as objectionable:

        %s
        
        (content type: %s, pk: %s)
        """ % (request.user.get_profile().name, url, content_type, pk)
        subject = "Abuse Report"
        try:
            profile = UserProfile.objects.get(email=settings.ADMINS[0][1])
            SendUserEmail.apply_async(args=(profile, subject, body))
        except:
            pass
        return render_to_response('drumbeat/report_received.html', {},
                                  context_instance=RequestContext(request))
    else:
        form = AbuseForm()
    return render_to_response('drumbeat/report_abuse.html', {
        'form': form,
        'content_type': content_type,
        'pk': pk,
    }, context_instance=RequestContext(request))
