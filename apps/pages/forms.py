from django import forms


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
