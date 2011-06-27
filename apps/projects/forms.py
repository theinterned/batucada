import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from drumbeat.utils import CKEditorWidget
from links.models import Link
from users.models import UserProfile
from users import tasks

from projects.models import Project
from projects import drupal


log = logging.getLogger(__name__)


class CreateProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'kind', 'short_description',
            'long_description', 'school', 'not_listed')
    widgets = {
        'long_description': CKEditorWidget(config_name='reduced'),
    }


class ProjectForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('name', 'kind', 'short_description',
            'long_description', 'school')
    widgets = {
        'long_description': CKEditorWidget(config_name='reduced'),
    }


class ProjectLinksForm(forms.ModelForm):

    class Meta:
        model = Link
        fields = ('name', 'url', 'subscribe')


class ProjectImageForm(forms.ModelForm):

    class Meta:
        model = Project
        fields = ('image',)

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            msg = _("Image exceeds max image size: %(max)dk")
            raise forms.ValidationError(msg % dict(max=max_size))
        return self.cleaned_data['image']


class ProjectStatusForm(forms.ModelForm):

    start_date = forms.DateField(localize=True, required=False)
    end_date = forms.DateField(localize=True, required=False)

    class Meta:
        model = Project
        fields = ('start_date', 'end_date', 'under_development',
            'not_listed', 'signup_closed', 'archived')


class ProjectAddParticipantForm(forms.Form):
    user = forms.CharField()
    organizer = forms.BooleanField(required=False)

    def __init__(self, project, *args, **kwargs):
        super(ProjectAddParticipantForm, self).__init__(*args, **kwargs)
        self.project = project

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = UserProfile.objects.get(username=username)
            if user.deleted:
                raise forms.ValidationError(
                    _('That user account was deleted.'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                _('There is no user with username: %s.') % username)
        # do not use is_organizing or is_participating here,
        # so superusers can join the study groups.
        if self.project.organizers().filter(user=user).exists():
            raise forms.ValidationError(
                _('User %s is already an organizer.') % username)
        is_participant = self.project.non_organizer_participants().filter(
            user=user).exists()
        if is_participant:
            raise forms.ValidationError(
                _('User %s is already a participant.') % username)
        return user


class ProjectContactOrganizersForm(forms.Form):
    """
    A modified version of ``messages.forms.ComposeForm`` that enables
    authenticated users to send a message to all of the organizers.
    """
    project = forms.IntegerField(required=True, widget=forms.HiddenInput())
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
                _('That study group, course, ... does not exist.'))
        recipients = project.organizers()
        subject = "[%s] " % project.name[:20] + self.cleaned_data['subject']
        body = render_to_string(
            "projects/emails/contact_organizer.txt", {
            'body': self.cleaned_data['body'],
            'domain': Site.objects.get_current().domain,
            'project': project}).strip()
        messages = [(sender, r.user.user, subject, body, parent_msg)
            for r in recipients]
        tasks.SendUsersEmail.apply_async(args=(self, messages))
        return messages


class CloneProjectForm(forms.Form):
    project = forms.CharField()

    def __init__(self, school=None, *args, **kwargs):
        super(CloneProjectForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_project(self):
        slug = self.cleaned_data['project']
        msg = _('There is no study group, course, ... with short name: %s.')
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise forms.ValidationError(msg % slug)
        if self.school and project.school != self.school:
            msg = _('The %(slug)s %(kind)s is not part of this school.')
            raise forms.ValidationError(msg % {'slug': slug,
                'kind': project.kind})
        return project


class ImportProjectForm(forms.Form):
    course = forms.CharField()

    def __init__(self, school=None, *args, **kwargs):
        super(ImportProjectForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_course(self):
        slug = self.cleaned_data['course']
        course = drupal.get_course(slug, full=True)
        if not course:
            raise forms.ValidationError(
                _('There is no course with this short name on the archive.'))
        if self.school and course['school'] != self.school:
            msg = _('The %s course was not part of this school.')
            raise forms.ValidationError(msg % slug)
        return course
