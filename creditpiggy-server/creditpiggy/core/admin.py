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

from django.contrib import admin
from creditpiggy.core.models import *

from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

# Register your models here.
admin.site.register(PiggyUser)
admin.site.register(ComputingUnit)

admin.site.register(Campaign)
admin.site.register(CampaignUserCredit)
admin.site.register(CampaignProject)

class PiggyProjectAdmin(admin.ModelAdmin):
	list_display = ('display_name', 'uuid', 'image', 'project_url')

	def image(self, obj):
		return mark_safe('<img src="%s" style="width: 32px; vertical-align: absmiddle" />' % obj.profile_image)

admin.site.register(PiggyProject, PiggyProjectAdmin)

class AchievementAdminForm(ModelForm):
	def clean_metrics(self):
		# Try to parse json
		try:
			json.loads( self.cleaned_data["metrics"] )
		except Exception as e:
			raise ValidationError("Error parsing JSON: %r" % e)
		# Return data
		return self.cleaned_data["metrics"]

class AchievementAdmin(admin.ModelAdmin):
	form = AchievementAdminForm
	list_display = ('name', 'image', 'metric_values')

	def image(self, obj):
		return mark_safe('<img src="%s" style="width: 32px; vertical-align: absmiddle" />' % obj.icon)

	def metric_values(self, obj):
		a = ""
		for k,v in obj.getMetrics().iteritems():
			a += "<li>%s >= <strong>%i</strong></li>" % (k,int(v))
		return mark_safe("<ul>%s<ul>" % a)

admin.site.register(Achievement, AchievementAdmin)

class ProjectUserRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'project', 'role', 'firstAction' , 'lastAction')
	list_filter = ('role',)

admin.site.register(ProjectUserRole, ProjectUserRoleAdmin)

class CreditSlotAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'status', 'project', 'credits', 'minBound', 'maxBound')
	list_filter = ('status',)

admin.site.register(CreditSlot, CreditSlotAdmin)

class AchievementInstanceAdmin(admin.ModelAdmin):
	list_display = ('achievement', 'user', 'project', 'campaign', 'date')
	list_filter = ('achievement','user','project','campaign')

admin.site.register(AchievementInstance, AchievementInstanceAdmin)

class WebsiteAdmin(admin.ModelAdmin):
	list_display = ('name', 'short', 'image')

	def image(self, obj):
		return mark_safe('<img src="%s" style="width: 32px; vertical-align: absmiddle" />' % obj.icon)

admin.site.register(Website, WebsiteAdmin)
