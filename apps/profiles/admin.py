from django.contrib import admin

from profiles.models import (Profile, ContactNumber, Link,
                             Skill, Interest)

class ProfileAdmin(admin.ModelAdmin):
    pass

class ContactNumberAdmin(admin.ModelAdmin):
    pass

class LinkAdmin(admin.ModelAdmin):
    pass

class SkillAdmin(admin.ModelAdmin):
    pass

class InterestAdmin(admin.ModelAdmin):
    pass

admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactNumber, ContactNumberAdmin)
admin.site.register(Link, LinkAdmin)
admin.site.register(Skill, SkillAdmin)
admin.site.register(Interest, InterestAdmin)
