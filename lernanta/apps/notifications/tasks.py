import datetime

from l10n.models import localize_email

from celery.task import Task


class SendNotifications(Task):
    """Send email notification to the users specified by ``profiles``."""
    name = 'notifications.tasks.SendNotifications'

    def run(self, profiles, subject_template, body_template, context, **kwargs):
        log = self.get_logger(**kwargs)
        subjects, bodies = localize_email(subject_template,
            body_template, context)
        for profile in profiles:
            if profile.deleted:
                continue
            subject = subjects[profile.preflang]
            body = bodies[profile.preflang]
            log.debug("Sending email to user %d with subject %s" % (
                profile.user.id, subject,))
            profile.user.email_user(subject, body)
