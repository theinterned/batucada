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
        fields = ('title', 'content', 'collaborative', 'publish')
        widgets = {
            'content': CKEditorWidget(config_name=CKEDITOR_CONFIG_NAME),
        }


class OwnersNotListedPageForm(forms.ModelForm):

    class Meta:
        model = Page
        fields = ('content', 'collaborative', 'publish')
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
        
         
    def clean(self): 
        data = self.cleaned_data 
        if 'content' in data and self.cleaned_data['content'].strip() == "<br />":
            # Adding error message here but it doesn't show because of ckeditor? It is also in views.py
            self._errors['id_content'] = forms.util.ErrorList("Comments cannot be empty")
        return data

