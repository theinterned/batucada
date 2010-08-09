from django.contrib import admin
from users.models import *

class ProfileAdmin(admin.ModelAdmin):
    pass

class ProfilePhoneNumber(admin.ModelAdmin):
    pass

class ProfileLinkAdmin(admin.ModelAdmin):
    pass

class ProfileSkillAdmin(admin.ModelAdmin):
    pass

class ProfileInterestAdmin(admin.ModelAdmin):
    pass

class ConfirmationTokenAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ProfileLink, ProfileLinkAdmin)
admin.site.register(ProfileSkill, ProfileSkillAdmin)
admin.site.register(ProfileInterest, ProfileInterestAdmin)
admin.site.register(ConfirmationToken, ConfirmationTokenAdmin)
