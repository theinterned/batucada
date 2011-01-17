from django import forms

from statuses.models import Status


class StatusForm(forms.ModelForm):

    class Meta:
        model = Status
        fields = ('project', 'status')
