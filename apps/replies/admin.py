from django.contrib import admin

from replies.models import PageComment


class PageCommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('id', 'page', 'author', 'created_on', 'deleted')
    list_filter = list_display[3:]
    search_fields = ('id', 'page__slug', 'page__title',
        'author__username', 'author__full_name')


admin.site.register(PageComment, PageCommentAdmin)
