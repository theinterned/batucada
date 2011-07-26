from django import forms

from replies.models import PageComment


class CommentForm(forms.ModelForm):

    class Meta:
        model = PageComment
        fields = ('content',)
