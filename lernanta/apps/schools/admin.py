from django.contrib import admin
from schools.models import School


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    search_fields = ('id', 'name',)

admin.site.register(School, SchoolAdmin)
