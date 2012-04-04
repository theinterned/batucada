import datetime

from l10n.models import localize_email

from celery.task import Task

from messages.models import Message


class SendNotifications(Task):
    """Send email notification to the users specified by ``profiles``."""
    name = 'users.tasks.SendNotifications'

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


class SendPrivateMessages(Task):
    """
    Send a private message to multiple users. ``messages`` should be a sequence
    containing tuples of sender, recipient, subject, body, parent.
    """
    name = 'users.tasks.SendPrivateMessages'

    def run(self, form, messages, **kwargs):
        log = self.get_logger(**kwargs)
        log.debug("Sending email to %d user(s)." % (len(messages),))
        for message in messages:
            (sender, recipient, subject, body, parent) = message
            msg = Message(sender=sender, recipient=recipient,
                          subject=subject, body=body)
            if parent is not None:
                msg.parent_msg = parent
                parent.replied_at = datetime.datetime.now()
                parent.save()
            msg.save()
