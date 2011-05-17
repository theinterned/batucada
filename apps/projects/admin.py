from django.contrib import admin
from projects.models import Project


class ProjectAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('name', 'created_on', 'school', 'featured',
        'under_development', 'not_listed', 'signup_closed', 
        'archived')
    list_filter = list_display[1:]
    search_fields = ('name',)


admin.site.register(Project, ProjectAdmin)

