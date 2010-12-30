from celery.task import Task


class SendUserEmail(Task):

    def run(self, profile, subject, body, **kwargs):
        log = self.get_logger(**kwargs)
        log.debug("Sending email to user %d with subject %s" % (
            profile.user.id, subject,))
        profile.user.email_user(subject, body)
