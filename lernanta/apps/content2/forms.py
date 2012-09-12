from django import forms

class ContentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea)

