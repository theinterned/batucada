from django import forms

from ckeditor.widgets import CKEditorWidget

from content.models import Page


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

