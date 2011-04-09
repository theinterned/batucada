from django import forms

from drumbeat.utils import CKEditorWidget

from content.models import Page, PageComment


CKEDITOR_CONFIG_NAME = 'rich'


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }


class NotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }


class OwnersPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'collaborative',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'collaborative',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = PageComment
        fields = ('content',)
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }
