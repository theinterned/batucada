from django import forms
from django.conf import settings

class CourseCreationForm(forms.Form):
    title = forms.CharField()
    short_title = forms.CharField()
    plug = forms.CharField(widget=forms.Textarea)
    language = forms.ChoiceField(choices=settings.LANGUAGES)

