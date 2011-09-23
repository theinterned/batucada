from django.contrib import admin

from badges.models import Badge, Rubric

class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')

class RubricAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'badge')

admin.site.register(Badge, BadgeAdmin)
admin.site.register(Rubric, RubricAdmin)