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

# Register your models here.
admin.site.register(PiggyUser)
admin.site.register(ComputingUnit)
admin.site.register(PiggyProject)
admin.site.register(ProjectUserCredit)
admin.site.register(ProjectCredentials)
admin.site.register(Achievement)
admin.site.register(AchievementInstance)
admin.site.register(Campaign)
admin.site.register(CampaignUserCredit)
admin.site.register(CampaignProject)

class ProjectUserRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'project', 'role')

admin.site.register(ProjectUserRole, ProjectUserRoleAdmin)

class CreditSlotAdmin(admin.ModelAdmin):
	list_display = ('uuid', 'status', 'project', 'credits', 'minBound', 'maxBound')
	list_filter = ('status',)

admin.site.register(CreditSlot, CreditSlotAdmin)
