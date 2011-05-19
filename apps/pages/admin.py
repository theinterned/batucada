from django.contrib import admin

from pages.models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'content')
    list_filter = list_display[6:]

admin.site.register(Page, PageAdmin)
