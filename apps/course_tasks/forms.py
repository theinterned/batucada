from django import forms
from django.forms.extras.widgets import SelectDateWidget

from course_tasks.models import CourseTask


class TaskForm(forms.ModelForm):

    class Meta:
        model = CourseTask
        fields = ('project', 'title', 'description', 'due_on')
        widgets = {
            'project': forms.HiddenInput(),
            'description': forms.Textarea(attrs={'cols': 12, 'rows': 55}),
        }
