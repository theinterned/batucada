from django import forms

from drumbeat.utils import CKEditorWidget

from schools.models import School


class SchoolForm(forms.ModelForm):

    class Meta:
        model = School
        fields = ('name', 'description')
	widgets = {
		'description': CKEditorWidget(config_name='rich'),
	}
