from django import forms
from django.utils.translation import ugettext as _

from drumbeat.utils import CKEditorWidget
from projects.models import Project
from users.models import UserProfile

from schools.models import School


class SchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('name', 'description')
	widgets = {
		'description': CKEditorWidget(config_name='rich'),
	}


class SchoolImageForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('image',)

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            raise forms.ValidationError(
                _("Image exceeds max image size: %(max)dk") % dict(max=max_size))
        return self.cleaned_data['image']


class ProjectAddOrganizerForm(forms.Form):
    user = forms.CharField()

    def __init__(self, school, *args, **kwargs):
        super(ProjectAddOrganizerForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_user(self):
        username = self.cleaned_data['user']
        try:
            user = UserProfile.objects.get(username=username)
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(_('There is no user with username: %s.') % username)
        if self.school.organizers.filter(id=user.id).exists():
            raise forms.ValidationError(_('User %s is organizing the school.') % username)
        return user


class SchoolAddFeaturedForm(forms.Form):
    project = forms.CharField()

    def __init__(self, school, *args, **kwargs):
        super(SchoolAddFeaturedForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_project(self):
        slug = self.cleaned_data['project']
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise forms.ValidationError(_('There is no study group with that short name: %s.') % slug)
        if project.school != self.school:
            raise forms.ValidationError(_('The %s study group is not part of this school.') % slug)
        if self.school.featured.filter(slug=slug).exists():
            raise forms.ValidationError(_('The %s study group is already featured for this school.') % slug)
        return project


class SchoolAddDeclinedForm(forms.Form):
    project = forms.CharField()

    def __init__(self, school, *args, **kwargs):
        super(SchoolAddDeclinedForm, self).__init__(*args, **kwargs)
        self.school = school

    def clean_project(self):
        slug = self.cleaned_data['project']
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            raise forms.ValidationError(_('There is no study group with that short name: %s.') % slug)
        if project.school != self.school:
            raise forms.ValidationError(_('The %s study group is not part of this school.') % slug)
        if self.school.featured.filter(slug=slug).exists():
            raise forms.ValidationError(_('The %s study group was already declined for this school.') % slug)
        return project
