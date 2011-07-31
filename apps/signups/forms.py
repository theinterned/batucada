from django import forms

from signups.models import Signup, SignupAnswer


class SignupForm(forms.ModelForm):

    class Meta:
        model = Signup
        fields = ('status', 'public', 'between_participants')


class SignupAnswerForm(forms.ModelForm):

    class Meta:
        model = SignupAnswer
        fields = ('standard', 'public', 'between_participants')
