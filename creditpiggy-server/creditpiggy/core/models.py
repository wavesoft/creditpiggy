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

import uuid
import time
import json
import random
import pytz
import datetime

from django.db import models, transaction
from django.contrib.auth.models import AbstractUser
from creditpiggy.core.metrics import MetricsModelMixin
from creditpiggy.core.housekeeping import HousekeepingTask, periodical

from tinymce.models import HTMLField

###################################################################
# Utlity Functions
###################################################################

def gen_token_key():
	"""
	Token key generator
	"""
	# Token charset
	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
	key = ""
	for i in range(0, 48):
		key += charset[random.randint(0, len(charset)-1)]
	# Return a unique key
	return key

def new_token():
	"""
	UUID Generator
	"""
	return uuid.uuid4().hex

def new_uuid():
	"""
	UUID Generator
	"""
	return uuid.uuid4().hex

def to_dict(instance):
	"""
	Convert a model isinstance to dictionary
	"""
	opts = instance._meta
	data = {}
	for f in opts.concrete_fields + opts.many_to_many:
		if isinstance(f, models.ManyToManyField):
			if instance.pk is None:
				data[f.name] = []
			else:
				data[f.name] = list(f.value_from_object(instance).values_list('pk', flat=True))
		else:
			data[f.name] = f.value_from_object(instance)
	return data

###################################################################
# Database Models
###################################################################

class PiggyUser(MetricsModelMixin, AbstractUser):
	"""
	Public profile of the user. One or more Social Authentiion back-ends
	can be linked to this profile.
	"""

	#: Time zones
	TIMEZONES = [ (x,x) for x in pytz.all_timezones ]

	#: Metrics information
	METRICS_FEATURES = {
		"credits" 			: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/allocated"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/completed"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/discarded"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
	}

	#: The UUID of this user, used for analytics purposes
	uuid = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="Unique user identification string")

	#: How the user will be visible to the public
	display_name = models.CharField(max_length=200, default="")

	#: The user's timezone
	timezone = models.CharField(max_length=255, default="UTC", choices=TIMEZONES)

	def profile(self):
		"""
		Compile and return the relevant information for the user's profile
		"""

		return {
			"id": self.uuid,
			"display_name": self.display_name.strip(),
			"counters": self.metrics().counters()
		}


class Achievement(models.Model):
	"""
	A target goal that can be achieved 
	"""

	#: Name of the achievement
	name = models.CharField(max_length=200, default="",
		help_text="Name of the achievement")

	#: A short description for the achievement
	desc = HTMLField(
		help_text="Achievement short text")

	#: Visual details: Icon of the achievement badge
	icon = models.CharField(max_length=200, default="")

	#: Visual details: Color of the achievement badge
	color = models.CharField(max_length=24, default="#662D91")

	#: Visual details: Shape of the frame
	frame_type = models.CharField(max_length=8, default="circle")

	#: How many times this achievement can be given
	instances = models.IntegerField(default=0)

	#: The time after which it expires
	expires = models.IntegerField(default=0)

	#: Metrics required for this achievement as a JSON field
	metrics = models.TextField(default="{}")

	def __unicode__(self):
		return self.name

	def getMetrics(self):
		"""
		Return metrics json
		"""
		return json.loads(self.metrics)

class ComputingUnit(MetricsModelMixin, models.Model):
	"""
	A computing unit that can bring credits to a user.
	"""

	#: Computing unit UUID
	uuid = models.CharField(max_length=32, default="", unique=True, db_index=True, 
		help_text="A unique ID generated from within the computing unit and delivered to CP through the batch system")

	#: Owner of this computing unit
	owner = models.ForeignKey( PiggyUser, default=None, null=True )

class PiggyProject(MetricsModelMixin, models.Model):
	"""
	THe project ID
	"""

	#: Metrics information
	METRICS_FEATURES = {
		"credits" 			: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/allocated"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/completed"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/discarded"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
	}

	#: Project UUID
	uuid = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="A unique ID identifying the specified project")

	#: The visual name of the project
	display_name = models.CharField(max_length=1024, 
		help_text="Project's full name")

	#: A short description for this project
	desc = HTMLField(
		help_text="Project description")

	#: The icon of this project
	profile_image = models.CharField(max_length=1024, 
		help_text="Project's profile image")

	#: Project URL
	project_url = models.URLField(default="", blank=True)

	#: Achievements related to this project
	achievements = models.ManyToManyField( Achievement, blank=True )

	def __unicode__(self):
		return u"%s" % self.display_name

	def achievementStatus(self, user=None):
		"""
		Return the achievement with their status
		"""

		ans = []
		for a in self.achievements.all():

			# Count achievement instances
			if user is None:

				# Just count how many instances we have
				ans.append({
						"achievement": a,
						"instances": AchievementInstance.objects.filter(project=self, achievement=a).count()
					})

				# Sort by instances
				ans = sorted(ans, lambda x,y: y['instances'] - x['instances'] )

			else:

				# Check if the user has it
				try:
					achoeved = AchievementInstance.objects.get(project=self, achievement=a, user=user)
				except AchievementInstance.DoesNotExist:
					achoeved = None

				# Include additional meta
				ans.append({
						"achievement": a,
						"achieved": achoeved
					})

				# Achieved first
				ans = sorted(ans, lambda x,y: int(bool(y['achieved'])) - int(bool(x['achieved'])) )

		# Return achievements and their status
		return ans

class Website(MetricsModelMixin, models.Model):
	"""
	A website that can use creditpiggy
	"""

	#: Name of the website
	name = models.CharField(max_length=200, default="",
		help_text="Name of the website")

	#: A short description for the website
	desc = HTMLField(
		help_text="Short description")

	#: A short description for the website
	short = models.CharField(max_length=200, default="")

	#: Visual details: Icon of the login splash
	icon = models.CharField(max_length=200, default="")

	#: The projects this website host
	projects = models.ManyToManyField( PiggyProject )

	def __unicode__(self):
		return self.name

class ProjectUserRole(MetricsModelMixin, models.Model):
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

	#: First action (timestamp)
	firstAction = models.DateTimeField(auto_now_add=True)

	#: Last action (timestamp)
	lastAction = models.DateTimeField(auto_now=True)

	#: The credits of the user in this model
	credits = models.IntegerField(default=0)

class CreditSlot(MetricsModelMixin, models.Model):
	"""
	A slot allocated and claimed by the server
	"""

	# Roles
	FREE = 0
	CLAIMED = 1
	DISCARDED = 2

	# Choices
	STATUS = (
		(FREE, 'Free'),
		(CLAIMED, 'Claimed'),
		(DISCARDED, 'Discarded'),
	)

	# The slot unique ID
	uuid = models.CharField(max_length=256, unique=False, db_index=True, 
		help_text="The globally unique slot ID as specified by the project owner")

	# The UNIX timestamp after which the slot is considered 'expired'
	expireTime = models.IntegerField(default=0)

	# The project associated with this credits slot
	project = models.ForeignKey( PiggyProject )

	# The credits associated to this slot
	credits = models.IntegerField(null=True, default=None, blank=True)

	# The minimum boundary of credits associated to this slot
	minBound = models.IntegerField(null=True, default=None, blank=True)

	# The maximum boundary of credits associated to this slot
	maxBound = models.IntegerField(null=True, default=None, blank=True)

	#: The status of the slot
	status = models.IntegerField( choices=STATUS, default=FREE )

	#: Discard reason
	reason = models.CharField(max_length=32, null=True, default=None, blank=True) 

class Campaign(MetricsModelMixin, models.Model):
	"""
	Campaigns are 
	"""
	
	#: Metrics information
	METRICS_FEATURES = {
		"credits" 			: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/allocated"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/completed"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
		"slots/discarded"	: ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
	}

	#: Name of the campaign
	name = models.CharField(max_length=200, default="",
		help_text="Name of the campaign")

	#: A short description for the achievement
	desc = HTMLField(
		help_text="Campaign description")

	#: Start date unix timestamp
	start_time = models.DateTimeField(default=datetime.datetime.now)

	#: End date unix timestamp
	end_time = models.DateTimeField(default=datetime.datetime.now)

	#: True if the campaign is published
	published = models.BooleanField(default=False)

	#: True if the campaign is activated
	active = models.BooleanField(default=False)

	@classmethod
	def ofProject(cls, project, active=False):
		"""
		Return all the Campaigns containing this project
		"""
		
		# Get all valid campaigns for this project
		if active:
			return CampaignProject.objects.filter( 
				campaign__start_time__gte=datetime.datetime.now(), 
				campaign__end_time__lte=datetime.datetime.now(),
				campaign__active=True,
				campaign__published=True,
				project=project
				)

		else:
			return CampaignProject.objects.filter( 
				project=project
				)

class CampaignUserCredit(MetricsModelMixin, models.Model):
	"""
	Credits given to a user for the participation in the campaign
	"""

	#: The user
	user = models.ForeignKey( PiggyUser )

	#: The project
	campaign = models.ForeignKey( Campaign )

	#: The credits of the user in this model
	credits = models.IntegerField(default=0)

	#: Achievements related to this campaign
	achievements = models.ManyToManyField( Achievement )

class CampaignProject(models.Model):
	"""
	ManyToManyField relation to projects
	"""

	#: The campaign
	campaign = models.ForeignKey(Campaign)

	#: The project
	project = models.ForeignKey(PiggyProject)

class AchievementInstance(models.Model):
	"""
	An achievement instance for a user/project combination
	"""

	#: The user that achieved it
	user = models.ForeignKey(PiggyUser)

	#: The project for which he/she achieved it
	project = models.ForeignKey(PiggyProject)

	#: Optionally, a related campaign to this acvievement
	campaign = models.ForeignKey(Campaign, blank=True, null=True, default=None)

	#: The achievement achieved
	achievement = models.ForeignKey(Achievement)

	#: The date he/she achieved it
	date = models.DateTimeField(auto_now_add=True)

	def __unicode__(self):
		return "%s/%s for %s" % (self.achievement.name, self.project.display_name, self.user.display_name)

###################################################################
# Utility Classes
###################################################################

# This module requires the above models
import creditpiggy.core.credits as credits

class ModelHousekeeping(HousekeepingTask):
	"""
	Housekeeping tasks for the models
	"""

	@periodical(hours=1)
	def expire_slots(self):
		"""
		Expire credit slots
		"""

		# Perform multiple atomic requests in an atomic transaction
		with transaction.atomic():

			# Expire all slots with timestamp bigger than the current
			for slot in CreditSlot.objects.filter( credits__gt = int(time.time()) ):

				# Discard slot
				credits.discard_slot( slot, 'expired' )

				# Delete slot
				slot.delete()
