from django.contrib import admin
from relationships.models import Relationship


class RelationshipAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('id', 'source', 'target_user', 'target_project', 'created_on')
    list_filter = ('created_on',)
    search_fields = ('id', 'source__username', 'source__full_name', 'target_user__username',
        'target_user__full_name', 'target_project__name', 'target_project__slug')


admin.site.register(Relationship, RelationshipAdmin)
