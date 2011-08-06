from django import forms

from statuses.models import Status


class ImportantStatusForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = ('status', 'important')


class StatusForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = ('status',)
