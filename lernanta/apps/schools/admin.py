from django.contrib import admin
from django.utils.translation import ugettext as _

from schools.models import School, ProjectSet, ProjectSetIndex


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('id', 'name',)

admin.site.register(School, SchoolAdmin)

class ProjectSetIndexInline(admin.TabularInline):
    model = ProjectSetIndex

class ProjectSetAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school',)
    search_fields = ('id', 'name', 'school__name',)
    inlines = (ProjectSetIndexInline,)

admin.site.register(ProjectSet, ProjectSetAdmin)
