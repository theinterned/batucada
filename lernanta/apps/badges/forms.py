from django import forms
from django.forms.models import inlineformset_factory

from badges.models import Badge, Submission, Assessment, Rating


class BadgeForm(forms.ModelForm):

    class Meta:
        model = Badge
        fields = ('name', 'description', 'image',
            'assessment_type', 'badge_type', 'rubrics')
        widgets = {
            'assessment_type': forms.RadioSelect,
            'badge_type': forms.RadioSelect,
        }


class SubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('url', 'content',)


class AssessmentForm(forms.ModelForm):

    class Meta:
        model = Assessment
        fields = ('comment',)


class RatingForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ('score',)
        widgets = {
            'score': forms.RadioSelect,
        }
