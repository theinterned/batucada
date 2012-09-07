from django import forms

class CourseCreationForm(forms.Form):
    title = forms.CharField()
    short_title = forms.CharField()
    plug = forms.CharField()
