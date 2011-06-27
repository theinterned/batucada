from django import forms

from pages.models import Page


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
