from django.contrib import admin
from projects.models import Project, Participation


class ProjectAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('name', 'created_on', 'school', 'featured',
        'under_development', 'not_listed', 'signup_closed', 
        'archived')
    list_filter = list_display[1:]
    search_fields = ('name', 'slug', 'school__name')

class ParticipationAdmin(admin.ModelAdmin):
    date_hierarchy = 'joined_on'
    list_display = ('user', 'project', 'organizing', 'joined_on',
        'left_on', 'no_wall_updates', 'no_updates')
    list_filter = list_display[2:]
    search_fields = ('project__name', 'user__username', 'user__full_name', 'project__slug')

admin.site.register(Project, ProjectAdmin)
admin.site.register(Participation, ParticipationAdmin)

