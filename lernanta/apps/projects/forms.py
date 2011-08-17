import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string

from links.models import Link
from users.models import UserProfile
from users import tasks
from tags.forms import GeneralTagField
from tags.models import GeneralTaggedItem

from projects.models import Project
from projects import drupal


log = logging.getLogger(__name__)


class ProjectForm(forms.ModelForm):
    tags = GeneralTagField(required=False)

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        if kwargs.has_key('instance'):
            instance = kwargs['instance']
            self.initial['tags'] = GeneralTaggedItem.objects.filter(
               object_id=instance.id)

    class Meta:
        model = Project
        fields = ('name', 'category', 'other', 'other_description',
            'short_description', 'long_description')
        widgets = {
            'category': forms.RadioSelect,
        }

    def clean_other(self):
        data = self.cleaned_data
        other = data.get('other')
        other_provided = (other and other.strip())
        if data.get('category') == Project.OTHER and not other_provided:
            raise forms.ValidationError(_('This field is required.'))
        return other.strip() if other else other

    def clean(self):
        super(ProjectForm, self).clean()
        data = self.cleaned_data
        if data.get('category') != Project.OTHER:
            data['other'] = ''
            data['other_description'] = ''
        return data

    def save(self, commit=True):
        model = super(ProjectForm, self).save(commit=False)
        if commit:
            model.save()
            model.tags.set(*self.cleaned_data['tags'])
            model.save()
        return model


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
            'not_listed', 'archived')


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
        tasks.SendPrivateMessages.apply_async(args=(self, messages))
        return messages


class CloneProjectForm(forms.Form):
    project = forms.CharField()

    def clean_project(self):
        slug = self.cleaned_data['project']
        msg = _('There is no study group, course, ... with short name: %s.')
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise forms.ValidationError(msg % slug)
        return project


class ImportProjectForm(forms.Form):
    course = forms.CharField()

    def clean_course(self):
        slug = self.cleaned_data['course']
        course = drupal.get_course(slug, full=True)
        if not course:
            raise forms.ValidationError(
                _('There is no course with this short name on the archive.'))
        return course
