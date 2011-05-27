from django.contrib import admin
from users.models import UserProfile


class UserProfileAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_on'
    list_display = ('id', 'username', 'full_name', 'email', 'location',
        'preflang', 'featured', 'created_on')
    list_filter = list_display[5:]
    search_fields = list_display[:5]

admin.site.register(UserProfile, UserProfileAdmin)
