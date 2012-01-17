from django.contrib import admin

from badges.models import Badge, Rubric, Award, Logic
from badges.models import Submission, Assessment, Rating


class BadgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')


class RubricAdmin(admin.ModelAdmin):
    list_display = ('id', 'question')


class AwardAdmin(admin.ModelAdmin):
    pass


class LogicAdmin(admin.ModelAdmin):
    pass


class SubmissionAdmin(admin.ModelAdmin):
    pass


class AssessmentAdmin(admin.ModelAdmin):
    pass


class RatingAdmin(admin.ModelAdmin):
    pass

admin.site.register(Badge, BadgeAdmin)
admin.site.register(Rubric, RubricAdmin)
admin.site.register(Award, AwardAdmin)
admin.site.register(Logic, LogicAdmin)
admin.site.register(Submission, SubmissionAdmin)
admin.site.register(Assessment, AssessmentAdmin)
admin.site.register(Rating, RatingAdmin)
