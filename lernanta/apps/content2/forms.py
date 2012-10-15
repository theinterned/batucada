from django import forms
from content2 import utils

class ContentForm(forms.Form):
    title = forms.CharField()
    content = forms.CharField(widget=forms.Textarea, required=False)

    def clean_content(self):
        return utils.clean_user_content(self.cleaned_data['content'])
