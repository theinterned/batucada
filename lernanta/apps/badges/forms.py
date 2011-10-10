from django import forms
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from badges.models import Badge, Submission, Assessment


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
        fields = ('comment', )
