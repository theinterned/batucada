import logging

from django import forms
from django.conf import settings
from django.forms.extras.widgets import SelectDateWidget
from django.utils.translation import ugettext_lazy as _

from challenges.models import (Challenge, Submission, Judge,
                               VoterTaxonomy, VoterDetails)
from messages.models import Message
from users.models import UserProfile

log = logging.getLogger(__name__)


class ChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        exclude = ('slug', 'project', 'created_by', 'created_on', 'is_open')
        widgets = {
            'start_date': SelectDateWidget(),
            'end_date': SelectDateWidget(),
        }


class ChallengeImageForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ('image',)

    def clean_image(self):
        if self.cleaned_data['image'].size > settings.MAX_IMAGE_SIZE:
            max_size = settings.MAX_IMAGE_SIZE / 1024
            raise forms.ValidationError(
                _("Image exceeds max image size: %(max)dk",
                  dict(max=max_size)))
        return self.cleaned_data['image']


class ChallengeContactForm(forms.Form):
    challenge = forms.IntegerField(required=True, widget=forms.HiddenInput())
    subject = forms.CharField(label=_(u'Subject'))
    body = forms.CharField(
        label=_(u'Body'),
        widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'}),
    )

    def save(self, sender):
        challenge = self.cleaned_data['challenge']
        try:
            challenge = Challenge.objects.get(id=int(challenge))
        except Challenge.DoesNotExist:
            raise forms.ValidationError(_(u'Not a valid challenge'))
        recipients = UserProfile.objects.filter(submissions__challenge=challenge).distinct()
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender=sender,
                recipient=r.user,
                subject=subject,
                body=body,
            )
            msg.save()
            message_list.append(msg)
        return message_list


class SubmissionSummaryForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('summary', )


class SubmissionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('title', 'summary', 'keywords', 'bio')


class SubmissionDescriptionForm(forms.ModelForm):

    class Meta:
        model = Submission
        fields = ('description', )
        widgets = {
            'description': forms.Textarea(attrs={'class': 'wmd'}),
        }


class VoterDetailsForm(forms.ModelForm):
    taxonomy = forms.ModelMultipleChoiceField(
        queryset=VoterTaxonomy.objects.all(),
        required=True, widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = VoterDetails
        fields = ('taxonomy', )

    def clean_taxonomy(self):
        if len(self.cleaned_data['taxonomy']) > 3:
            raise forms.ValidationError('Select no more than 3.')
        return self.cleaned_data['taxonomy']


class JudgeForm(forms.ModelForm):
    class Meta:
        model = Judge
        fields = ('user', )
