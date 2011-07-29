from django.contrib import admin

from replies.models import PageComment


class PageCommentAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('id', 'author', 'scope_content_type',
        'page_content_type', 'created_on', 'deleted')
    list_filter = list_display[3:]
    search_fields = ('id', 'author__username', 'author__full_name',
        'scope_content_type__model', 'scope_content_type__app_label',
        'page_content_type__model', 'page_content_type__app_label')


admin.site.register(PageComment, PageCommentAdmin)
