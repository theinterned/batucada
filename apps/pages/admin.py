from django.contrib import admin

from pages.models import Page


class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug')
    search_fields = ('id', 'title', 'slug', 'content')

admin.site.register(Page, PageAdmin)
