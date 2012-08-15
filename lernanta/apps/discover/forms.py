import logging

from django import forms
from django.conf import settings
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.db.models import Count

from schools.models import School

from discover.models import get_active_languages

log = logging.getLogger(__name__)

class ProjectsFilterForm(forms.Form):
    # Not Listed by Default
    archived = forms.BooleanField(required=False, widget=forms.HiddenInput)
    under_development = forms.BooleanField(required=False, widget=forms.HiddenInput)
    closed_signup = forms.BooleanField(required=False, widget=forms.HiddenInput)
    # Filter Links
    COMMUNITY = 'community'
    SHOWCASE = 'showcase'
    FRESH = 'fresh'
    POPULAR = 'popular'
    UPDATED = 'updated'
    FEATURED_CHOICES = (
        (COMMUNITY, _('Community Picks')),
        (SHOWCASE, _('Showcase')),
        (FRESH, _('Fresh Additions')),
        (POPULAR, _('Popular')),
        (UPDATED, _('Last Updated'))
    )
    featured = forms.ChoiceField(required=False, widget=forms.HiddenInput,
        choices=FEATURED_CHOICES)
    school = forms.ModelChoiceField(required=False, queryset=School.objects.all(),
        widget=forms.HiddenInput)
    tag = forms.CharField(required=False, widget=forms.HiddenInput)
    # Filter Form
    language = forms.ChoiceField(required=False, choices=[('all', 'All')] + get_active_languages())
    reviewed = forms.BooleanField(required=False)


class SearchPreferenceForm(forms.Form):
    search_language = forms.ChoiceField(required=False, choices=[('all', 'All')] + get_active_languages())
    reviewed = forms.BooleanField(required=False)
