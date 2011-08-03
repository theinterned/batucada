from django.shortcuts import render_to_response
from django.template import RequestContext

from users.decorators import login_required
from projects.models import Project
from schools.models import School


@login_required
def chat(request):
    profile = request.user.get_profile()
    nick = 'p2pu-%s' % profile.username
    channels = set(['p2pu-community'])
    for project in profile.following(Project):
        if not project.not_listed:
            channels.add('p2pu-%s-%s' % (project.id, project.slug[:10]))
            if project.school:
                channels.add('p2pu-%s' % project.school.slug)
    for school in School.objects.all():
        if school.organizers.filter(username=profile.username):
            channels.add('p2pu-%s' % school.slug)
    return render_to_response('chat/chat.html', {
        'nick': nick,
        'channels': ','.join(channels)},
        context_instance=RequestContext(request))
