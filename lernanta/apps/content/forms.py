from django import forms

from content.models import Page


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'minor_update',)


class NotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'minor_update',)


class OwnersPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'collaborative', 'minor_update')


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'collaborative', 'minor_update')
