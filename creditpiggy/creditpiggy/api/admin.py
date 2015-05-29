import hashlib
from django.contrib import admin

# from creditpiggy.frontend.models import PiggyUser
# from creditpiggy.api.models import CreditCache, AuthToken, ProjectAuthToken

# admin.site.register(ProjectAuthToken)

# class CreditCacheAdmin(admin.ModelAdmin):
# 	list_display = ('user', 'project', 'credit')

# admin.site.register(CreditCache, CreditCacheAdmin)

# class AuthTokenAdmin(admin.ModelAdmin):
# 	fields = ('user', 'auth_key', 'auth_salt', 'auth_hash', 'tokenType')
# 	readonly_fields = ('auth_key','auth_salt')
# 	list_display = ('auth_key', 'user')
# 	def save_model(self, request, obj, form, change):
# 		"""
# 		Calculate auth_hash when saving the record
# 		"""
# 		obj.user = PiggyUser.objects.get(id=request.POST['user'])
# 		obj.tokenType = request.POST['tokenType']
# 		obj.auth_hash = hashlib.sha512("%s:%s" % (obj.auth_salt, request.POST['auth_hash'])).hexdigest()
# 		obj.save()

# admin.site.register(AuthToken, AuthTokenAdmin)
