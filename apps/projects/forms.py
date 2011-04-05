import datetime
import logging

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext as _

from links.models import Link
from messages.models import Message
from projects.models import Project, ProjectMedia, Participation
from users.models import UserProfile

log = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'short_description', 'long_description')


class ProjectDescriptionForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('detailed_description',)
        widgets = {
            'detailed_description': forms.Textarea(attrs={'class': 'wmd'}),
        }


class ProjectLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url',)


class ProjectImageForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('image',)

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            raise forms.ValidationError(
                _("Image exceeds max image size: %(max)dk",
                  dict(max=max_size)))
        return self.cleaned_data['image']


class ProjectMediaForm(forms.ModelForm):

    allowed_content_types = (
        'video/ogg',
        'video/webm',
        'video/mp4',
        'application/ogg',
        'audio/ogg',
        'image/png',
        'image/jpg',
        'image/jpeg',
        'image/gif',
    )

    class Meta:
        model = ProjectMedia
        fields = ('project_file',)

    def clean_project_file(self):
        content_type = self.cleaned_data['project_file'].content_type
        if not content_type in ProjectMedia.accepted_mimetypes:
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
                _(u'That study group does not exist.'))
        recipients = project.participants()
        subject = "[p2pu-%s] " % project.slug + self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient=r.user.user,
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


class ProjectPreparationStatusForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('preparation_status',)


class ProjectAddParticipantForm(forms.Form):
    user = forms.CharField()

    def __init__(self, project, *args, **kwargs):
        super(ProjectAddParticipantForm, self).__init__(*args, **kwargs)
        self.project = project

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(_('There is no user with username: %s.') % username)
        if user == self.project.created_by:
            raise forms.ValidationError(_('User %s is organizing the study group.') % username)
        try:
            participation = self.project.participants().get(user=user)
            raise forms.ValidationError(_('User %s is already a participant.') % username)
        except Participation.DoesNotExist:
            pass
        return user



