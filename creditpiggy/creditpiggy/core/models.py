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


from django.db import models
from django.contrib.auth.models import AbstractUser
from creditpiggy.core.metrics import MetricsModelMixin

import uuid
import random

def new_uuid():
	"""
	UUID Generator
	"""
	return uuid.uuid4().hex

def gen_token_key():
	"""
	Token key generator
	"""
	# Token charset
	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
	key = ""
	for i in range(0, 48):
		key += charset[random.randint(0, len(charset)-1)]
	# Return a unique key
	return key

class PiggyUser(MetricsModelMixin, AbstractUser):
	"""
	Public profile of the user. One or more Social Authentiion back-ends
	can be linked to this profile.
	"""

	#: How the user will be visible to the public
	display_name = models.CharField(max_length=200, default="")

class ComputingUnit(MetricsModelMixin, models.Model):
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

class PiggyProject(MetricsModelMixin, models.Model):
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
	Credentials for each project
	"""

	#: Authentication token
	token = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="Anonymous authentication token for the credentials")

	#: Shared secret between
	secret = models.CharField(max_length=48, default=gen_token_key, 
		help_text="Shared secret between project and administrator")

	#: The project
	project = models.ForeignKey( PiggyProject )


class CreditSlot(MetricsModelMixin, models.Model):
	"""
	A slot allocated and claimed by the server
	"""

	# The slot unique ID
	uuid = models.CharField(max_length=256, unique=False, db_index=True, 
		help_text="The globally unique slot ID as specified by the project owner")

	# The project associated with this credits slot
	project = models.ForeignKey( PiggyProject )

	# The credits associated to this slot
	credits = models.IntegerField(null=True, default=None)

	# The minimum boundary of credits associated to this slot
	minBound = models.IntegerField(null=True, default=None)

	# The maximum boundary of credits associated to this slot
	maxBound = models.IntegerField(null=True, default=None)