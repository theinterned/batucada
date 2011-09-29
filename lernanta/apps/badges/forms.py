from django import forms

from badges.models import Badge, Submission


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
        fields = ('content',)