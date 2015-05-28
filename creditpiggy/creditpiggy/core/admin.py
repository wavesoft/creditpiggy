from django.contrib import admin
from creditpiggy.core.models import UserProfile, AuthUser

# Register your models here.

admin.site.register(UserProfile)
admin.site.register(AuthUser)
