from django.contrib import admin

from relationships.models import UserRelationship

class UserRelationshipAdmin(admin.ModelAdmin):
    pass

admin.site.register(UserRelationship, UserRelationshipAdmin)
