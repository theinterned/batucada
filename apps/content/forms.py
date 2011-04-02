from django import forms

from ckeditor.widgets import CKEditorWidget

from content.models import Page, PageComment


class PageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content',)
        widgets = {
            'content': CKEditorWidget(),
        }


class NotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content',)
        widgets = {
            'content': CKEditorWidget(),
        }


class OwnersPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('title', 'content', 'collaborative',)
        widgets = {
            'content': CKEditorWidget(),
        }


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'collaborative',)
        widgets = {
            'content': CKEditorWidget(),
        }


class CommentForm(forms.ModelForm):

    class Meta:
        model = PageComment
        fields = ('content',)
        widgets = {
            'content': CKEditorWidget(),
        }
