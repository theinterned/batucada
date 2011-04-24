from django.contrib import admin
from content.models import Page, PageVersion, PageComment


admin.site.register(Page)
admin.site.register(PageVersion)
admin.site.register(PageComment)
