from django.contrib import admin

from tracker.models import PageView


class PageViewAdmin(admin.ModelAdmin):
    date_hierarchy = 'access_time'
    list_display = ('id', 'session_key', 'user', 'access_time',
        'request_url', 'referrer_url', 'ip_address', 'time_on_page')
    list_filter = ('access_time',)
    search_fields = ('id', 'session_key', 'user__username', 'user__full_name',
        'request_url', 'referrer_url', 'ip_address')


admin.site.register(PageView, PageViewAdmin)
