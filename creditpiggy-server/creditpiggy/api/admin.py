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

import json
import hashlib
from django.contrib import admin
from django.forms import ModelForm
from django.core.exceptions import ValidationError

from creditpiggy.api.models import *

class ProjectCredentialsAdmin(admin.ModelAdmin):
	list_display = ('project', 'token')

admin.site.register(ProjectCredentials, ProjectCredentialsAdmin)

class WebsiteCredentialsForm(ModelForm):
	def clean_domains(self):

		# Try to parse json
		try:
			json.loads( self.cleaned_data["domains"] )
		except Exception as e:
			raise ValidationError("Error parsing JSON: %r" % e)

		# Return data
		return self.cleaned_data["domains"]

class WebsiteCredentialsAdmin(admin.ModelAdmin):
	list_display = ('website', 'token', 'authorized_domains')
	form = WebsiteCredentialsForm

	def authorized_domains(self, obj):
		return ", ".join(obj.getDomains())

admin.site.register(WebsiteCredentials, WebsiteCredentialsAdmin)
