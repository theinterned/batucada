from django import forms
from django.db import models
from django.forms.models import inlineformset_factory
from django.utils.translation import ugettext as _

from users.models import UserProfile
from richtext.models import RichTextField

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


class AssessmentForm(forms.Form):
    submission = forms.IntegerField(required=True, widget=forms.HiddenInput())
    comment = forms.CharField(
                    label = _(u'Comment'),
                    widget = forms.Textarea(attrs={'rows': '12', 'cols': '55'}),
                    )
    widgets = {
               'ratings': forms.RadioSelect,
               }

    def __init__(self, submission, *args, **kwargs):
        super(AssessmentForm, self).__init__(*args, **kwargs)
        self.submission = submission
        self.badge = submission.badge
    
        rubrics = submission.badge.rubrics.all()
        ratings = []
        for rubric in rubrics:
            ratings.append(Rating(rubric=rubric))
        self.ratings = ratings


class PeerAssessmentForm(forms.ModelForm):
    peer = forms.CharField()

    class Meta:
        model = Assessment
        fields = ('comment',)

    def __init__(self, badge, profile, *args, **kwargs):
        super(PeerAssessmentForm, self).__init__(*args, **kwargs)
        self.badge = badge
        self.profile = profile

    def clean_peer(self):
        username = self.cleaned_data['peer']
        if self.profile.username == username:
            raise forms.ValidationError(
                 _('You cannot give a badge to yourself.'))
        try:
            user = UserProfile.objects.get(username=username)
            if user.deleted:
                raise forms.ValidationError(
                    _('That user account was deleted.'))
        except UserProfile.DoesNotExist:
            raise forms.ValidationError(
                _('There is no user with username: %s.') % username)
        if not self.badge.get_peers(self.profile).filter(id=user.id).exists():
            raise forms.ValidationError(
                _('User %s needs to be your peer.') % username)
        return user


class RatingForm(forms.ModelForm):

    class Meta:
        model = Rating
        fields = ('score',)
        widgets = {
            'score': forms.RadioSelect,
        }
