import datetime
import logging

from django import forms
from django.forms.extras.widgets import SelectDateWidget

from challenges.models import Challenge, Submission, Judge

log = logging.getLogger(__name__)

class ChallengeForm(forms.ModelForm):
  class Meta:
    model = Challenge
    exclude = ('slug', 'project', 'created_by', 'created_on', 'is_open')
    widgets = {
      'start_date': SelectDateWidget(),
      'end_date': SelectDateWidget(),      
    }

class SubmissionForm(forms.ModelForm):

  class Meta:
    model = Submission
    fields = ('title', 'summary', 'description')
    widgets = {
      'description': forms.Textarea(attrs={'class': 'wmd'}),
    }


class JudgeForm(forms.ModelForm):
  class Meta:
    model = Judge
    fields = ('user', )
