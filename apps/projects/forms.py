from django import forms

from projects.models import Project

class ProtectedProjectForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProtectedProjectForm, self).__init__(*args,**kwargs)
        
        protected = getattr(self.Meta, 'protected')
        project = kwargs.get('instance', None)

        if not project.featured:
            for field in protected:
                self.fields.pop(field)

class ProjectForm(ProtectedProjectForm):
    class Meta:
        model = Project
        exclude = ('created_by', 'slug', 'featured')
        protected = ('template', 'css')

