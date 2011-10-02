from django import forms

from content.models import Page


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'sub_header', 'content', 'minor_update',)


class NotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'sub_header', 'minor_update',)


class OwnersPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'sub_header', 'content',
            'collaborative', 'minor_update')


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'sub_header', 'collaborative', 'minor_update')
