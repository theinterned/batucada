from django import forms
from django.utils.translation import ugettext as _

from drumbeat.utils import CKEditorWidget
from projects.models import Project

from schools.models import School


class SchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('name', 'description')
	widgets = {
		'description': CKEditorWidget(config_name='rich'),
	}


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
