from django import forms
from django.conf import settings

class CourseCreationForm(forms.Form):
    title = forms.CharField()
    short_title = forms.CharField()
    plug = forms.CharField(widget=forms.Textarea)
    language = forms.ChoiceField(choices=settings.LANGUAGES)


class CourseUpdateForm(forms.Form):
    title = forms.CharField(required=False)
    short_title = forms.CharField(required=False)
    plug = forms.CharField(widget=forms.Textarea, required=False)
    language = forms.ChoiceField(choices=settings.LANGUAGES, required=False)


class CourseImageForm(forms.Form):
    image = forms.ImageField()


class CourseLanguageForm(forms.Form):
    language = forms.ChoiceField(choices=settings.LANGUAGES)


class CourseTermForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
