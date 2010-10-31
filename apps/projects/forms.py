import datetime

from django import forms
from django.utils.translation import ugettext as _

from messages.models import Message
from projects.models import Project

class ProtectedProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProtectedProjectForm, self).__init__(*args,**kwargs)
        
        protected = getattr(self.Meta, 'protected')
        project = kwargs.get('instance', None)

        if project and not project.featured:
            for field in protected:
                self.fields.pop(field)

class ProjectForm(ProtectedProjectForm):
    class Meta:
        model = Project
        exclude = ('created_by', 'slug', 'featured')
        protected = ('template', 'css')

class ProjectContactUsersForm(forms.Form):
    """
    A modified version of ``messages.forms.ComposeForm`` that enables
    project admins to send a message to all of the users who follow
    their project.
    """
    project = forms.IntegerField(
        required=True,
        widget=forms.HiddenInput()
    )
    subject = forms.CharField(label=_(u'Subject'))
    body = forms.CharField(
        label=_(u'Body'),
        widget=forms.Textarea(attrs={'rows': '12', 'cols': '55'})
    )

    def save(self, sender, parent_msg=None):
        project = self.cleaned_data['recipient']
        try:
            project = Project.objects.get(id=int(project))
        except Project.DoesNotExist:
            raise forms.ValidationError(_(u'Hmm, that does not look like a valid project'))
        recipients = project.followers()
        subject = self.cleaned_data['subject']
        body = self.cleaned_data['body']
        message_list = []
        for r in recipients:
            msg = Message(
                sender = sender,
                recipient = r,
                subject = subject,
                body = body,
            )
            if parent_msg is not None:
                msg.parent_msg = parent_msg
                parent_msg.replied_at = datetime.datetime.now()
                parent_msg.save()
            msg.save()
            message_list.append(msg)
        return message_list
