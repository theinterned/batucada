from django import forms

from badges.models import Badge

class BadgeForm(forms.ModelForm):

    class Meta:
        model = Badge
        fields = ('name', 'description', 'image', 'criteria',
            'assessment_type', 'badge_type')
        widgets = {
            'assessment_type': forms.RadioSelect,
            'badge_type': forms.RadioSelect,
        }
