from django.contrib import admin

from tracker.models import PageView


class PageViewAdmin(admin.ModelAdmin):
    date_hierarchy = 'access_time'
    list_display = ('id', 'session_key', 'user', 'access_time',
        'request_url', 'referrer_url', 'ip_address', 'time_on_page',
        'user_agent')
    list_filter = ('access_time',)
    search_fields = ('id', 'session_key', 'user__username',
        'request_url', 'referrer_url', 'ip_address', 'user_agent')


admin.site.register(PageView, PageViewAdmin)
