from django.contrib import admin

from badges.models import Badge

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')

admin.site.register(Badge, BadgeAdmin)