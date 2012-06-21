import datetime

from l10n.models import localize_email

from django.conf import settings

from celery.task import Task


class SendNotifications(Task):
    """Send email notification to the users specified by ``profiles``."""
    name = 'notifications.tasks.SendNotifications'

    def run(self, profiles, subject_template, body_template, context, reply_token=None, **kwargs):
        log = self.get_logger(**kwargs)
        subjects, bodies = localize_email(subject_template,
            body_template, context)
            
        from_email = setting.DEFAULT_FROM_EMAIL
        if reply_token:
            from_email = "reply+{0}@{1}".format(reply_token,
                settings.REPLY_EMAIL_DOMAIN)
            
        for profile in profiles:
            if profile.deleted:
                continue
            subject = subjects[profile.preflang]
            body = bodies[profile.preflang]
            log.debug("Sending email to user %d with subject %s" % (
                profile.user.id, subject,))
            profile.user.email_user(subject, body, from_email)
