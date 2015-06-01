################################################################
# CreditPiggy - Volunteering Computing Credit Bank Project
# Copyright (C) 2015 Ioannis Charalampidis
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
################################################################

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
