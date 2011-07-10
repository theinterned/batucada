from django import forms

from statuses.models import Status
from drumbeat.utils import CKEditorWidget


class ImportantStatusForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = ('status', 'important')
        widgets = {
            'status': CKEditorWidget(config_name='reduced'),
        }


class StatusForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = ('status',)
        widgets = {
            'status': CKEditorWidget(config_name='reduced'),
        }
