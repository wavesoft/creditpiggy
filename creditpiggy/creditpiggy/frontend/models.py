from django.db import models
from django.conf import settings
#import uuid

# def project_uuid():
# 	"""
# 	UUID Generator
# 	"""
# 	return uuid.uuid4().hex

# class PiggyUser(models.Model):
# 	"""
# 	Extended user profile
# 	"""
# 	user = models.OneToOneField(settings.AUTH_USER_MODEL)
# 	display_name = models.CharField(max_length=200)
# 	email = models.CharField(max_length=200)

# 	def __unicode__(self):
# 		return u"%s (%s)" % (self.display_name, self.user.username)

# class Project(models.Model):
# 	"""
# 	THe project ID
# 	"""
# 	name = models.CharField(max_length=50, unique=True, help_text="A short identifier for the project")
# 	display_name = models.CharField(max_length=200, help_text="Project's full name")
# 	contact = models.CharField(max_length=500, help_text="The associated website for this project")

# 	def __unicode__(self):
# 		return u"%s (%s)" % (self.display_name, self.name)

# class ProjectRevision(models.Model):
# 	"""
# 	Various revisions of the main project
# 	"""

# 	uuid = models.CharField(max_length=32, default=project_uuid, unique=True, db_index=True, help_text="A unique key for this project version")
# 	project = models.ForeignKey('Project')
# 	revision = models.IntegerField()
	
# 	project_text = models.TextField()
# 	website = models.CharField(max_length=500, help_text="The associated website for this project")

# 	def __unicode__(self):
# 		return u"%s (rev %s)" % (self.project.name, self.revision)

# class ProjectMember(models.Model):
# 	"""
# 	Links between projects and people in projects
# 	"""
# 	OWNER = 'OW'
# 	ADMIN = 'AD'
# 	MODERATOR = 'MO'
# 	MEMBER = 'ME'
# 	MEMBER_ROLE = (
# 		(OWNER, 'Owner'),
# 		(ADMIN, 'Administrator'),
# 		(MODERATOR, 'Moderator'),
# 		(MEMBER, 'Member'),
# 	)
# 	user = models.ForeignKey('PiggyUser')
# 	project = models.ForeignKey('ProjectRevision')
# 	role = models.CharField(max_length=2, choices=MEMBER_ROLE, default=MEMBER)
