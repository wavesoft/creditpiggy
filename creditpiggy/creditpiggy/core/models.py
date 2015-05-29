from django.db import models
from django.contrib.auth.models import AbstractUser
from creditpiggy.core.analytics import AnalyticsModelMixin
import uuid

def new_uuid():
	"""
	UUID Generator
	"""
	return uuid.uuid4().hex

class PiggyUser(AnalyticsModelMixin, AbstractUser):
	"""
	Public profile of the user. One or more Social Authentiion back-ends
	can be linked to this profile.
	"""

	#: How the user will be visible to the public
	display_name = models.CharField(max_length=200, default="")

class ComputingUnit(AnalyticsModelMixin, models.Model):
	"""
	A computing unit that can bring credits to a user.
	"""

	#: Computing unit UUID
	uuid = models.CharField(max_length=32, default="", unique=True, db_index=True, 
		help_text="A unique ID generated from within the computing unit and delivered to CP through the batch system")

	#: Owner of this computing unit
	owner = models.ForeignKey( PiggyUser, default=None, null=True )

	#: Analytics registry
	### ???

class PiggyProject(models.Model):
	"""
	THe project ID
	"""

	#: Project UUID
	uuid = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="A unique ID identifying the specified project")

	#: The visual name of the project
	display_name = models.CharField(max_length=1024, 
		help_text="Project's full name")

	#: A short description for this project
	desc = models.TextField(
		help_text="Project description")

	#: The icon of this project
	profileImage = models.CharField(max_length=1024, 
		help_text="Project's profile image")

	def __unicode__(self):
		return u"%s" % self.display_name

class ProjectUserRole(models.Model):
	"""
	The relationship between a user and a project
	"""

	# Roles
	OWNER = 0
	ADMIN = 1
	MODERATOR = 2
	MEMBER = 3

	# Choices
	MEMBER_ROLE = (
		(OWNER, 'Owner'),
		(ADMIN, 'Administrator'),
		(MODERATOR, 'Moderator'),
		(MEMBER, 'Member'),
	)

	#: The user
	user = models.ForeignKey( PiggyUser )
	
	#: The project
	project = models.ForeignKey( PiggyProject )

	#: The relationship
	role = models.IntegerField( choices=MEMBER_ROLE, default=MEMBER )

class ProjectCredentials(models.Model):
	"""
	
	"""

class CreditSlot(models.Model):
	"""
	A slot 
	"""
	pass