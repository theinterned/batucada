from django import forms
from django.utils.translation import ugettext as _

from drumbeat.utils import CKEditorWidget
from content.models import Page, PageComment

CKEDITOR_CONFIG_NAME = 'rich'


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'minor_update',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if data.strip() == "<br />":
            raise forms.ValidationError(_("This field is required."))
        return data


class NotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'minor_update',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if data.strip() == "<br />":
            raise forms.ValidationError(_("This field is required."))
        return data


class OwnersPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'collaborative', 'minor_update')
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if data.strip() == "<br />":
            raise forms.ValidationError(_("This field is required."))
        return data


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'collaborative', 'minor_update')
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if data.strip() == "<br />":
            raise forms.ValidationError(_("This field is required."))
        return data


class CommentForm(forms.ModelForm):

    class Meta:
        model = PageComment
        fields = ('content',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }

    def clean_content(self):
        data = self.cleaned_data['content']
        if data.strip() == "<br />":
            raise forms.ValidationError(_("This field is required."))
        return data
