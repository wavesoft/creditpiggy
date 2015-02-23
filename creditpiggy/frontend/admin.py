from django.contrib import admin
from frontend.models import PiggyUser, Project, ProjectRevision, ProjectMember

# Register your models here.

admin.site.register(PiggyUser)
admin.site.register(Project)

class ProjectRevisionAdmin(admin.ModelAdmin):
	list_display = ('project', 'revision', 'uuid')
	readonly_fields = ('uuid',)

admin.site.register(ProjectRevision, ProjectRevisionAdmin)

class ProjectMemberAdmin(admin.ModelAdmin):
	list_display = ('user', 'project', 'role')

admin.site.register(ProjectMember, ProjectMemberAdmin)
