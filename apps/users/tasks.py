import datetime

from celery.task import Task

from messages.models import Message


class SendUserEmail(Task):
    """Send an email to a specific user specified by ``profile``."""

    def run(self, profile, subjects, bodies, **kwargs):
        if profile.deleted:
            return
        log = self.get_logger(**kwargs)
        subject = subjects[profile.preflang]
        body = bodies[profile.preflang]
        log.debug("Sending email to user %d with subject %s" % (
            profile.user.id, subject,))
        profile.user.email_user(subject, body)


class SendPrivateMessages(Task):
    """
    Send an email to multiple users. ``messages`` should be a sequence
    containing tuples of sender, recipient, subject, body, parent.
    """

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
