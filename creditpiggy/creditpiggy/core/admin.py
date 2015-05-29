from django.contrib import admin
from creditpiggy.core.models import PiggyUser, ComputingUnit, PiggyProject, ProjectUserRole, ProjectCredentials

# Register your models here.

admin.site.register(PiggyUser)
admin.site.register(ComputingUnit)
admin.site.register(PiggyProject)

class ProjectUserRoleAdmin(admin.ModelAdmin):
	list_display = ('user', 'project', 'role')

admin.site.register(ProjectUserRole, ProjectUserRoleAdmin)

admin.site.register(ProjectCredentials)
