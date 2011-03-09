from django import forms
from django.forms.extras.widgets import SelectDateWidget

from course_tasks.models import Todo


class TodoForm(forms.ModelForm):

    class Meta:
        model = Todo
        fields = ('project', 'title', 'description', 'due_on')
    

