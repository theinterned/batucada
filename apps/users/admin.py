from django.contrib import admin

from users.models import ConfirmationToken

class ConfirmationTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(ConfirmationToken, ConfirmationTokenAdmin)
