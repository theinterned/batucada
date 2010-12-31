import datetime
import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from messages.models import Message
from projects.models import Project, ProjectMedia

log = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'short_description', 'long_description')


class ProjectDescriptionForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('detailed_description',)


class ProjectMediaForm(forms.ModelForm):

    allowed_content_types = (
        'image/png',
        'image/jpeg',
        'image/gif',
        'video/ogg',
        'video/webm',
        'video/mp4',
        'application/ogg',
    )

    class Meta:
        model = ProjectMedia
        fields = ('project_file',)

    def clean_project_file(self):
        content_type = self.cleaned_data['project_file'].content_type
        if not content_type in self.allowed_content_types:
            log.warn("Attempt to upload unsupported file type: %s" % (
                content_type,))
            raise ValidationError(_('Unsupported file type.'))
        if self.cleaned_data['project_file'].size > settings.MAX_UPLOAD_SIZE:
            max_size = settings.MAX_UPLOAD_SIZE / 1024 / 1024
            raise ValidationError(
                _("File exceeds max file size: %(max)dMB" % {
                    'max': max_size,
                 }),
            )
        return self.cleaned_data['project_file']


class ProjectContactUsersForm(forms.Form):
    """
    A modified version of ``messages.forms.ComposeForm`` that enables
    project admins to send a message to all of the users who follow
    their project.
    """
    project = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput(),
    )
    subject = forms.CharField(label=_(u'Subject'))
    body = forms.CharField(
        label=_(u'Body'),
        widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'}),
    )

    def save(self, sender, parent_msg=None):
        project = self.cleaned_data['project']
        try:
            project = Project.objects.get(id=int(project))
        except Project.DoesNotExist:
            raise forms.ValidationError(
                _(u'Hmm, that does not look like a valid project'))
        recipients = project.followers()
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient=r.user,
                subject=subject,
                body=body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = datetime.datetime.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
        return message_list
