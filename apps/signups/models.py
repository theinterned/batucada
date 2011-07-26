from django.contrib.sites.models import Site

from users.tasks import SendUserEmail
from l10n.models import localize_email


def send_sign_up_notification(instance):
    """Send sign_up notifications."""
    if instance.page.slug != 'sign-up':
        return
    project = instance.page.project
    is_answer = not instance.reply_to
    context = {
        'comment': instance,
        'is_answer': is_answer,
        'project': project,
        'domain': Site.objects.get_current().domain,
    }
    subjects, bodies = localize_email(
        'signups/emails/sign_up_updated_subject.txt',
        'signups/emails/sign_up_updated.txt', context)
    recipients = {}
    for organizer in project.organizers():
        recipients[organizer.user.username] = organizer.user
    if instance.reply_to:
        comment = instance
        while comment.reply_to:
            comment = comment.reply_to
            recipients[comment.author.username] = comment.author
    for username in recipients:
        if recipients[username] != instance.author:
            SendUserEmail.apply_async((recipients[username],
                subjects, bodies))

