from django.contrib import admin

from relationships.models import Relationship

class RelationshipAdmin(admin.ModelAdmin):
    pass

admin.site.register(Relationship, RelationshipAdmin)
