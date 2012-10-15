from django import forms
from django.conf import settings

class CourseCreationForm(forms.Form):
    title = forms.CharField()
    hashtag = forms.CharField(max_length=20)
    description = forms.CharField(widget=forms.Textarea)
    language = forms.ChoiceField(choices=settings.LANGUAGES)


class CourseUpdateForm(forms.Form):
    title = forms.CharField(required=False)
    hashtag = forms.CharField(required=False, max_length=20)
    description = forms.CharField(widget=forms.Textarea, required=False)
    language = forms.ChoiceField(choices=settings.LANGUAGES, required=False)


class CourseImageForm(forms.Form):
    image = forms.ImageField()


class CourseTermForm(forms.Form):
    start_date = forms.DateField()
    end_date = forms.DateField()
