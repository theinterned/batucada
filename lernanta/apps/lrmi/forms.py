from django import forms


class LrmiForm(forms.Form):

    EDUCATIONAL_ROLE_CHOICES = [
        ('', 'not set'),
        ('student', 'Students'),
        ('teacher', 'Teachers'),
    ]

    INTERACTIVITY_CHOICES = [
        ('', 'not set'),
        ('active', 'Active'),
        ('expositive', 'Expositive'),
        ('mixed', 'Mixed'),
    ]

    educational_role = forms.ChoiceField(required=False, choices=EDUCATIONAL_ROLE_CHOICES)
    #educationalAlignment
    educational_use = forms.CharField(max_length=255, required=False)
    time_required = forms.CharField(max_length=255, required=False)
    typical_age_range = forms.CharField(max_length=255, required=False)
    interactivity_type = forms.ChoiceField(required=False, choices=INTERACTIVITY_CHOICES)
    is_based_on_url = forms.URLField(max_length=255, required=False)
    about = forms.CharField(max_length=255, required=False)
