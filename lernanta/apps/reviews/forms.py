from django import forms

from reviews.models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ('accepted', 'content', 'mark_deleted', 'mark_featured')
