from django.contrib import admin

from reviews.models import Review, Reviewer


class ReviewerAdmin(admin.ModelAdmin):
    pass

class ReviewAdmin(admin.ModelAdmin):
    pass

admin.site.register(Reviewer, ReviewerAdmin)
admin.site.register(Review, ReviewAdmin)
