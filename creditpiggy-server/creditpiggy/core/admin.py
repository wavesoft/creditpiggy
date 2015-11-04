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
from django.utils import timezone

from creditpiggy.core.models import *

from django.forms import ModelForm
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe

# Register your models here.

class PiggyUserPINLoginAdmin(admin.ModelAdmin):
	list_display = ('user', 'pin', 'allocated')

admin.site.register(PiggyUserPINLogin, PiggyUserPINLoginAdmin)


class PiggyUserAdmin(admin.ModelAdmin):
	list_display = ('id', 'username', 'display_name', 'timezone', 'profile', 'email_achievement', 'email_projects', 'email_surveys', 'priv_leaderboards')

	def profile(self, obj):
		return mark_safe('<img src="%s" style="width: 32px; vertical-align: absmiddle" />' % obj.profile_image)

admin.site.register(PiggyUser, PiggyUserAdmin)

class CampaignActiveFilter(admin.SimpleListFilter):
	title = 'Campaign Status'

	# Parameter for the filter that will be used in the URL query.
	parameter_name = 'campaign_status'

	def lookups(self, request, model_admin):
		return (
			('running', 'Running campaigns'),
		)

	def queryset(self, request, queryset):
		if self.value() == 'running':
			return queryset.filter(
				start_time__lte=timezone.now(), 
				end_time__gte=timezone.now(),
				active=True,
				published=True,
			)

class CampaignAdmin(admin.ModelAdmin):
	list_display = ('name', 'start_time', 'end_time', 'published', 'active', 'public', 'website', 'is_running')
	list_filter = (CampaignActiveFilter,)

	def is_running(self, obj):
		date_now = timezone.now()

		# Check for flags
		if (not obj.active):
			return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-no.gif"/> NO (Inactive)')
		if (not obj.published):
			return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-no.gif"/> NO (Unpublished)')

		# Check for date range
		if ((date_now >= obj.start_time) and (date_now <= obj.end_time)):
			delta = obj.end_time - date_now
			if delta.seconds < 60:
				return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-yes.gif"/> <strong>YES (%i sec left)</strong>' % delta.seconds)
			elif delta.seconds < 3600:
				return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-yes.gif"/> <strong>YES (%i min left)</strong>' % (delta.seconds / 60))
			elif delta.seconds < 86400:
				return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-yes.gif"/> <strong>YES (%i hours left)</strong>' % (delta.seconds / 3600))
			else:
				return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-yes.gif"/> <strong>YES (%i days left)</strong>' % (delta.seconds / 86400))
		else:
			return mark_safe('<img src="http://test.local:8000/static/admin/img/icon-no.gif"/> NO (Expired)')

admin.site.register(Campaign, CampaignAdmin)

class CampaignUserCreditAdmin(admin.ModelAdmin):
	list_display = ('user', 'campaign', 'credits')

admin.site.register(CampaignUserCredit, CampaignUserCreditAdmin)

class UserLinkLogsAdmin(admin.ModelAdmin):
	list_display = ('user', 'link_uuid', 'linked')

admin.site.register(UserLinkLogs, UserLinkLogsAdmin)

class ComputingUnitAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'owner', 'website', 'firstAction', 'lastAction')
	list_filter = ('owner',)

admin.site.register(ComputingUnit, ComputingUnitAdmin)

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
	list_display = ('name', 'image', 'metric_values', 'personal')
	list_filter = ('personal',)

	def image(self, obj):
		return mark_safe('<img src="%s" style="width: 32px; vertical-align: absmiddle" />' % obj.icon)

	def metric_values(self, obj):
		a = ""
		for k,v in obj.getMetrics().iteritems():
			a += "<li>%s >= <strong>%i</strong></li>" % (k,int(v))
		return mark_safe("<ul>%s<ul>" % a)

admin.site.register(Achievement, AchievementAdmin)

class PersonalAchievementAdmin(admin.ModelAdmin):
	list_display = ('user', 'achievement' , 'date')

admin.site.register(PersonalAchievement, PersonalAchievementAdmin)

class ReferralAdmin(admin.ModelAdmin):
	list_display = ('publisher', 'visitor' , 'visited')

admin.site.register(Referral, ReferralAdmin)

class ProjectUserRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'project', 'role', 'credits', 'norm_credits', 'firstAction' , 'lastAction')
	list_filter = ('role',)

admin.site.register(ProjectUserRole, ProjectUserRoleAdmin)

class CreditSlotAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'machine', 'project', 'credits', 'minBound', 'maxBound')
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

class VisualMetricAdmin(admin.ModelAdmin):
	list_display = ('name', 'display_name', 'priority', 'sum_method', 'units', 'icon')

admin.site.register(VisualMetric, VisualMetricAdmin)
