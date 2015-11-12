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
import logging
import hashlib
import urllib

from string import maketrans

from django.conf import settings
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone

from django.contrib.auth.models import AbstractUser

from creditpiggy.core.metrics import MetricsModelMixin
from creditpiggy.core.housekeeping import HousekeepingTask, periodical
from creditpiggy.core.image import image_colors
from creditpiggy.core.redis import share_redis_connection
from creditpiggy.core.email import send_custom_email

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

def gen_pin():
	"""
	PIN generator
	"""
	# Token charset
	charset = "0123456789"
	key = ""
	for i in range(0, 6):
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

def new_expire_time():
	"""
	Calculate the timestamp for the expire time of a new slot
	"""
	return time.time() + settings.CREDITPIGGY_CREDIT_EXPIRE_TIME

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

def achievement_from_share_id(share_id):
	"""
	Return the appropriate achievement according to it's ID
	"""

	# Try to parse
	try:
		achievement = int(share_id) & 0xffffff
	except ValueError:
		return None

	# Decrypt
	achievement = (achievement ^ settings.CREDITPIGGY_TRACKID_SECRET) & 0xffffff

	# Get type and ID
	a_type = achievement & 0x03
	a_id = achievement >> 2

	print "type=%i, id=%i" % (a_type, a_id)

	# lookup according to type
	if a_type == 1:
		try:
			return PersonalAchievement.objects.get(id=a_id)
		except PersonalAchievement.DoesNotExist:
			return None
	elif a_type == 2:
		try:
			return AchievementInstance.objects.get(id=a_id)
		except AchievementInstance.DoesNotExist:
			return None
	elif a_type == 3:
		try:
			return CampaignAchievementInstance.objects.get(id=a_id)
		except CampaignAchievementInstance.DoesNotExist:
			return None
	else:
		return None

def merge_accounts(self, user):
	"""
	Merge user 'user' to self
	"""

	logger = logging.getLogger("models.merge_accounts")

	# Log the link action
	logger.info("------- Link report ---------------------------")
	link = UserLinkLogs( user=self, link_uuid=user.uuid )
	link.save()
	logger.info(" - Created link log %s -> %s" % (user.uuid, self.uuid))

	# Import user metrics
	self.metrics().cincr( user.metrics().counters() )
	logger.info(" - Imported metric counters")

	# Find project-user correlations
	for pu in ProjectUserRole.objects.filter( user=user ):
		logger.info(" - Importing project/user role #%i" % pu.id)

		# Find or create my correlation
		mu = ProjectUserRole.objects.get_or_create( user=self, project=pu.project )
		logger.info(" -- Find matching role #%i" % mu.id)

		# Import credits & metrics
		mu.credits += pu.credits
		mu.metrics().cincr( pu.metrics().counters() )
		mu.save()
		logger.info(" -- Imported metric counters")

		# Delete pu
		pu.delete()

	# Adapt computing units
	for cu in ComputingUnit.objects.filter( owner=user ):
		logger.info(" - Claiming computing unit #%i" % cu.id)

		# Switch users
		cu.user = self
		cu.save()

		logger.info(" -- Switched ownership")

	# Adapt achievements
	for a in AchievementInstance.objects.filter( user=user ):
		logger.info(" - Claiming achievement #%i" % a.id)

		# Skip if I don't have that achievement
		if AchievementInstance.objects.filter( user=self, project=a.project, achievement=a.achievement ).exists():
			logger.info(" -- Already have it")
			continue

		# Switch ownership of the achievement
		a.user = self
		a.save()
		logger.info(" -- Switched ownership")

	logger.info("-----------------------------------------------")

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

	#: Profile picture
	profile_image = models.CharField(max_length=1024, default="",
		help_text="User's profile image")

	#: The user's timezone
	timezone = models.CharField(max_length=255, default="UTC", choices=TIMEZONES)

	#: E-mail options: Receive e-mail on achievement 
	email_achievement = models.BooleanField(default=True, help_text="Receive e-mail on achievement")

	#: E-mail options: Receive e-mail from project owners 
	email_projects = models.BooleanField(default=True, help_text="Receive e-mails from project owners")

	#: E-mail options: Receive e-mail for surveys 
	email_surveys = models.BooleanField(default=True, help_text="Receive e-mails for surveys")

	#: Privacy options: Show on leaderboards
	priv_leaderboards = models.BooleanField(default=True, help_text="Show on leaderboards")

	@staticmethod
	def fromAnonymousEmail(email, create=True):
		"""
		Create or fetch an anonymous user using his e-mail
		"""

		# Check if such user exits
		user = None
		created = False

		# Check if we should create missing user
		if create:
			(user, created) = PiggyUser.objects.get_or_create( email=email )
		else:
			try:
				user = PiggyUser.objects.get( email=email )
			except PiggyUser.DoesNotExist:
				return None

		# If that's a new user, set a random name
		if created:

			# Use e-mail as username
			user.username = "ano:%s" % email
			user.email = email

			# Pick an anonymous user name
			user.display_name = "Anonymous %s" % random.choice(settings.ANONYMOUS_NAMES).capitalize()

			# Try to use gravatar to get profile image
			user.profile_image = "//www.gravatar.com/avatar/" + hashlib.md5(email.lower()).hexdigest() + "?" + \
								 urllib.urlencode({'d':settings.ANONYMOUS_PROFILE_IMAGE, 's':str(64)})

			# Save 
			user.save()

		# Return user object
		return user


	@staticmethod
	def fromRef(refid):
		"""
		Get a user instance from the referral ID
		"""

		# Ensure format
		if refid[0] != 'r':
			return None

		# Decrypt and parse user ID
		try:
			userid = int(str(refid[1:]), 16) ^ settings.CREDITPIGGY_TRACKID_SECRET
		except ValueError:
			return None

		# Locate instance (and raise exception if not found)
		return PiggyUser.objects.get(id=userid)

	def ranking(self, base=1):
		"""
		Get overall user ranking
		"""

		# Get user ranking
		redis = share_redis_connection()
		rank = redis.zrevrank(
			"%srank/users" % (settings.REDIS_KEYS_PREFIX,),
			self.id
			)

		# If missing return None
		if rank is None:
			return None

		# Otherwise adapt to base-rank
		return rank + base

	def getRefererID(self):
		"""
		Return user's referer ID
		"""
		return "r%06x" % (self.id ^ settings.CREDITPIGGY_TRACKID_SECRET)

	def profile(self, website=None):
		"""
		Compile and return the relevant information for the user's profile
		"""

		# Get profile picture
		profile_img = self.profile_image
		if not profile_img:
			profile_img = settings.CREDITPIGGY_ANONYMOUS_PROFILE

		# Calculate a referrer ID, masked with a trackID secret
		# in order to keep it small.
		referrer = "r%06x" % (self.id ^ settings.CREDITPIGGY_TRACKID_SECRET)

		# Get ranking
		rank = None
		counters = None

		# Check if we should get per-website/campaign ranking
		if not website is None:

			# Get user's contribution on active campaigns
			campaign = Campaign.ofWebsite( website )
			user_campaigns = CampaignUserCredit.objects.filter( campaign=campaign[0], user=self )

			# Get ranking and counters of first campaign
			if user_campaigns.exists():
				rank = user_campaigns[0].ranking()
				counters = user_campaigns[0].metrics().counters()
			else:
				rank = 0
				counters = {}

		# Fallback to user ranking
		if rank is None:
			rank = self.ranking()
			counters = self.metrics().counters()

		# Return profile
		return {
			"id" 			: self.uuid,
			"ref"			: referrer,
			"rank"			: rank,
			"counters" 		: counters,
			"display_name" 	: self.display_name.strip(),
			"profile_image" : profile_img,
			"profile_url" 	: "javascript:;",
		}

	def achievementStatus(self, personal=True, unachieved=False):
		"""
		Return all the achievements of this user has achieved
		"""

		# List of achieved IDs
		achieved_ids = []

		# Get all achievements
		ans = []
		for a in AchievementInstance.objects.filter(user=self):

			# Collect IDs
			achieved_ids.append( a.achievement.id )

			# Include additional meta
			ans.append({
					"achievement": a.achievement,
					"achieved": True,
					"details": a,
					"project": a.project,
					"share_id": a.getShareID(),
				})

		# If we include personal, get them too
		for a in PersonalAchievement.objects.filter(user=self):

			# Collect IDs
			achieved_ids.append( a.achievement.id )

			# Include additional meta
			ans.append({
					"achievement": a.achievement,
					"achieved": True,
					"details": a,
					"project": None,
					"share_id": a.getShareID(),
				})

		# Check if we should include also unachieved
		if unachieved:
			for a in Achievement.objects.exclude( id__in=achieved_ids ):

				# Include additional meta
				ans.append({
						"achievement": a,
						"achieved": False,
						"details": None,
						"project": None,
					})

		# Return achievements and their status
		return ans

	def __unicode__(self):
		return self.display_name

class PiggyUserPINLogin(models.Model):
	"""
	PIN-Based log-in
	"""

	#: The user that requested the log-in
	user = models.OneToOneField( PiggyUser, db_index=True )

	#: The PIN allocated
	pin = models.CharField(max_length=32, default="")

	#: The time allocated
	allocated = models.DateTimeField(auto_now=True)

	#: SSO Token
	token = models.CharField(max_length=48, default=gen_token_key)

	@staticmethod
	def forUser(user):
		"""
		Create or get a user/pin correlation
		"""

		# Get pin login entity for this user
		(pinLogin, created) = PiggyUserPINLogin.objects.get_or_create( user=user )

		# Create new pin
		if created:
			pinLogin.pin = gen_pin()
			pinLogin.save()

		# Return entry
		return pinLogin

	def expired(self, timeout=60):
		"""
		Check if the specified token is expired
		"""

		# Get time delta
		delta = timezone.now() - self.allocated

		# Check if expired
		return delta.seconds > timeout


class Referral(models.Model):
	"""
	Referral log table
	"""

	#: The user that published the link
	publisher = models.ForeignKey( PiggyUser, related_name="user_publisher" )

	#: The user that visited the link
	visitor = models.ForeignKey( PiggyUser, related_name="user_visitor" )

	#: The time the user visited this entry
	visited = models.DateTimeField(auto_now_add=True)

class UserLinkLogs(models.Model):
	"""
	Log information regarding cross-user account linking 
	"""

	#: The current user ID
	user = models.ForeignKey( PiggyUser )

	#: The UUID of the link user
	link_uuid = models.CharField(max_length=32, default="")

	#: First action (timestamp)
	linked = models.DateTimeField(auto_now_add=True)

class VisualMetric(models.Model):
	"""
	A metric that can be shown to the user
	"""

	# Roles
	FIRST = 0
	ADD = 1
	AVERAGE = 2
	MINIMUM = 3
	MAXIMUM = 4

	# Choices
	SUM_METHOD = (
		(FIRST,   'Pick First'),
		(ADD, 	  'Add'),
		(AVERAGE, 'Average'),
		(MINIMUM, 'Minimum'),
		(MAXIMUM, 'Maximum'),
	)

	#: The name of the metric
	name = models.CharField(max_length=200, default="",
		help_text="The code name of the metric")

	#: The display name of the metric
	display_name = models.CharField(max_length=200, default="",
		help_text="How it's displayed to the user")

	#: The icon for the metric
	icon = models.CharField(max_length=200, default="",
		help_text="Metric icon (from fontawesome)")

	#: The units for this metric
	units = models.CharField(max_length=200, default="",
		help_text="Metric units")

	#: Summarization method
	sum_method = models.IntegerField( choices=SUM_METHOD, default=ADD )

	#: Values scale
	scale = models.FloatField(default=1.0, 
		help_text="Scale of the metrics value when presenting it")

	#: Number of decimals
	decimals = models.IntegerField(default=0, 
		help_text="Number of decimals when rounding the value before presenting it")

	#: Prority
	priority = models.IntegerField(default=0)

	def __unicode__(self):
		return "%s (%s)" % (self.name, self.display_name)

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

	#: If this achievement can be achieved in a personal level
	personal = models.BooleanField(default=False,
		help_text="This is something achieved in the user's personal metrics")

	#: If this achievement is for everyone in the host project/campaign/website
	team = models.BooleanField(default=False, 
		help_text="When used as a campaign or project achievement, grant this to each member of the campaign")

	def __unicode__(self):
		return self.name

	def getMetrics(self):
		"""
		Return metrics json
		"""
		return json.loads(self.metrics)

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
		"participate/users" : ( 'ts_hourly', 'ts_daily', 'ts_weekly', 'ts_monthly', 'ts_yearly' ),
	}

	#: Project UUID
	uuid = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="A unique ID identifying the specified project")

	#: URL ID, derrived from display_name
	slug = models.CharField(max_length=200, default="", db_index=True, editable=False,
		help_text="An indexing keyword, useful for human-readable URLs")

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
	
	#: Metrics to visualize	
	visual_metrics = models.ManyToManyField( VisualMetric, blank=True )

	#: Normalization factor
	norm_factor = models.FloatField( default=1.0 )

	def __unicode__(self):
		return u"%s" % self.display_name

	def ranking(self, base=1):
		"""
		Get overall project ranking
		"""

		# Get user ranking
		redis = share_redis_connection()
		rank = redis.zrevrank(
			"%srank/projects" % (settings.REDIS_KEYS_PREFIX,), 
			self.id
			)

		# If missing return None
		if rank is None:
			return None

		# Otherwise adapt to base-rank
		return rank + base

	def save(self, *args, **kwargs):
		"""
		Save model
		"""

		# Generate a URL-ID
		slug = str(self.display_name.lower())
		slug = slug.translate(maketrans(
				u" `~!@#$%^&*()_-+={[}]:;\"'<,>.?/\\|",
				u"---------------------------------"
			))

		# Include project ID to increase entropy
		self.slug = "%i-%s" % (self.id, slug)

		# Call super class
		return super(PiggyProject, self).save( *args, **kwargs )

	def achievementStatus(self, user=None, onlyAchieved=False):
		"""
		Return the achievement with their status
		"""

		ans = []
		for a in self.achievements.all():

			# Count achievement instances
			if user is None:

				# Count instances
				inst = AchievementInstance.objects.filter(project=self, achievement=a).count()

				# Just count how many instances we have
				ans.append({
						"achievement": a,
						"instances": inst,
						"project": self
					})

				# Sort by instances
				ans = sorted(ans, lambda x,y: y['instances'] - x['instances'] )

			else:

				# Check if the user has it
				try:
					achieved = AchievementInstance.objects.get(project=self, achievement=a, user=user)
					share_id = achieved.getShareID()
				except AchievementInstance.DoesNotExist:
					achieved = None
					share_id = None
					if onlyAchieved:
						continue

				# Include additional meta
				ans.append({
						"achievement": a,
						"achieved": not (achieved is None),
						"project": self,
						"details": achieved,
						"share_id": share_id,
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

	#: URL ID, derrived from display_name
	slug = models.CharField(max_length=200, default="", db_index=True, editable=False,
		help_text="An indexing keyword, useful for human-readable URLs")

	#: The website URL
	url = models.CharField(max_length=200, default="", blank=True,
		help_text="The website URL")

	#: A short description for the website
	desc = HTMLField(
		help_text="Short description")

	#: A short description for the website
	short = models.CharField(max_length=200, default="")

	#: Visual details: Icon of the login splash
	icon = models.CharField(max_length=200, default="")

	#: Visual details: Header image for the project
	header_image = models.CharField(max_length=200, default="")

	#: Visual details: Background color
	header_background = models.CharField(max_length=24, default="#660099")

	#: Visual details: Foreground color
	header_foreground = models.CharField(max_length=24, default="#fff")

	#: The projects this website host
	projects = models.ManyToManyField( PiggyProject )

	#: Metrics to visualize	
	visual_metrics = models.ManyToManyField( VisualMetric, blank=True )

	def save(self, *args, **kwargs):
		"""
		Save model
		"""

		# Generate a URL-ID
		slug = str(self.name.lower())
		slug = slug.translate(maketrans(
				u" `~!@#$%^&*()_-+={[}]:;\"'<,>.?/\\|",
				u"---------------------------------"
			))

		# Include project ID to increase entropy
		self.slug = "%i-%s" % (self.id, slug)

		# Process image colors from project header
		if self.header_image:
			(self.header_background, self.header_foreground) = \
				image_colors( self.header_image, default=None )

		# Call super class
		return super(Website, self).save( *args, **kwargs )

	def __unicode__(self):
		return self.name

class ComputingUnit(models.Model):
	"""
	A computing unit that can bring credits to a user.
	"""

	#: Computing unit UUID
	uuid = models.CharField(max_length=255, default="", unique=True, db_index=True, 
		help_text="A unique ID generated from within the computing unit and delivered to CP through the batch system")

	#: Owner of this computing unit
	owner = models.ForeignKey( PiggyUser, default=None, null=True )

	#: The website that triggered the claim
	website = models.ForeignKey( Website, default=None, null=True )

	#: First action (timestamp)
	firstAction = models.DateTimeField(auto_now_add=True)

	#: Last action (timestamp)
	lastAction = models.DateTimeField(auto_now=True)

	def __unicode__(self):
		return self.uuid

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

	#: The normalized of the user in this model
	norm_credits = models.FloatField(default=0.0)

	def ranking(self, base=1):
		"""
		Get user ranking in this project
		"""

		# Get user ranking
		redis = share_redis_connection()
		rank = redis.zrevrank(
			"%srank/project/%i/users" % (settings.REDIS_KEYS_PREFIX, self.project.id), 
			self.user.id
			)

		# If missing return None
		if rank is None:
			return None

		# Otherwise adapt to base-rank
		return rank + base

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

	#: The slot unique ID
	uuid = models.CharField(max_length=255, unique=False, db_index=True, 
		help_text="The globally unique slot ID as specified by the project owner")

	#: The machine claimed this slot
	machine = models.ForeignKey( ComputingUnit, null=True, default=None, blank=True )

	#: The UNIX timestamp after which the slot is considered 'expired'
	expireTime = models.IntegerField(default=new_expire_time)

	#: The project associated with this credits slot
	project = models.ForeignKey( PiggyProject )

	#: The credits associated to this slot
	credits = models.IntegerField(null=True, default=None, blank=True)

	#: The minimum boundary of credits associated to this slot
	minBound = models.IntegerField(null=True, default=None, blank=True)

	#: The maximum boundary of credits associated to this slot
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

	#: Website hosting this campaign
	website = models.ForeignKey( Website, default=None, null=True )

	#: True if the campaign is open to the public
	public = models.BooleanField(default=False)

	#: Achievements related to this campaign
	achievements = models.ManyToManyField( Achievement, blank=True )

	def expired(self):
		"""
		Check if the campaign is expired
		"""
		return self.end_time < timezone.now()

	def achievementStatus(self, unachieved=False):
		"""
		Return all the achievements of this user has achieved
		"""

		# List of achieved IDs
		achieved_ids = []

		# Get all achievements
		ans = []
		for a in CampaignAchievementInstance.objects.filter(campaign=self):

			# Collect IDs
			achieved_ids.append( a.achievement.id )

			# Include additional meta
			ans.append({
					"achievement": a.achievement,
					"achieved": True,
					"details": a,
					"campaign": self,
					"share_id": a.getShareID(),
				})

		# Check if we should include also unachieved
		if unachieved:
			for a in self.achievements.exclude( id__in=achieved_ids ):

				# Include additional meta
				ans.append({
						"achievement": a,
						"achieved": False,
						"campaign": self,
						"details": None,
					})

		# Return achievements and their status
		return ans


	@classmethod
	def ofWebsite(cls, website, active=True, expired=False):
		"""
		Return all the Campaigns addressing this website
		"""

		# Prepare query
		query = Campaign.objects.filter(
			website=website)

		# Mark active
		if active:
			query = query.filter(
				active=True, 
				published=True
				)

		# Check if we should include expired
		if not expired:
			query = query.filter(
				start_time__lte=timezone.now(), 
				end_time__gte=timezone.now(),
				)
		
		# Return query
		return query.order_by('-end_time')

	def __unicode__(self):
		return "%s" % (self.name)

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

	#: Achievements related to this user contribution to the campaign
	achievements = models.ManyToManyField( Achievement, blank=True )

	def ranking(self, base=1):
		"""
		Return user's ranking in this campaign
		"""

		# Get user ranking
		redis = share_redis_connection()
		rank = redis.zrevrank(
			"%srank/campaign/%i/users" % (settings.REDIS_KEYS_PREFIX, self.campaign.id),
			self.user.id
			)

		# If missing return None
		if rank is None:
			return None

		# Otherwise adapt to base-rank
		return rank + base

class PersonalAchievement(models.Model):
	"""
	An achievement instance linked to a user
	"""

	#: The user that achieved it
	user = models.ForeignKey(PiggyUser)

	#: The achievement achieved
	achievement = models.ForeignKey(Achievement)

	#: The date he/she achieved it
	date = models.DateTimeField(auto_now_add=True)

	def getShareID(self):
		"""
		Calculate an achievement sharable ID that makes it difficult
		to access other achievements (not impossible though)
		"""

		# Get share ID for AchievementInstance
		share_id = ((self.id << 2) | 0x01) & 0xffffff
		return "%010i" % (share_id ^ settings.CREDITPIGGY_TRACKID_SECRET)

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

	def getShareID(self):
		"""
		Calculate an achievement sharable ID that makes it difficult
		to access other achievements (not impossible though)
		"""

		# Get share ID for AchievementInstance
		share_id = ((self.id << 2) | 0x02) & 0xffffff
		return "%010i" % (share_id ^ settings.CREDITPIGGY_TRACKID_SECRET)

class CampaignAchievementInstance(models.Model):
	"""
	An achievement instance for a campaign
	"""

	#: The parent campaign
	campaign = models.ForeignKey( Campaign )

	#: The achievement achieved
	achievement = models.ForeignKey( Achievement )

	#: The time allocated
	date = models.DateTimeField(auto_now=True)

	def getShareID(self):
		"""
		Calculate an achievement sharable ID that makes it difficult
		to access other achievements (not impossible though)
		"""

		# Get share ID for AchievementInstance
		share_id = ((self.id << 2) | 0x03) & 0xffffff
		return "%010i" % (share_id ^ settings.CREDITPIGGY_TRACKID_SECRET)

class ManualEmail(models.Model):
	"""
	An e-mail sent from the interface non-automatically
	"""

	#: The date it was created
	created = models.DateTimeField(auto_now=True, editable=False)

	#: Subject of the e-mail
	subject = models.CharField(max_length=512, default="")

	#: A short description for the achievement
	body = HTMLField(help_text="The e-mail body")

	#: Target users
	target_user = models.ManyToManyField( PiggyUser, blank=True )

	#: Target campaigns
	target_campaign = models.ManyToManyField( Campaign, blank=True )

	#: Target project
	target_project = models.ManyToManyField( PiggyProject, blank=True )

	#: The date it was sent (or None if not sent)
	sent_date = models.DateTimeField(default=None, null=True, editable=False)

	#: A flag that denotes that this e-mail is draft and should not be sent 
	draft = models.BooleanField(default=True, help_text="Uncheck this to send the e-mail")

	def save(self, *args, **kwargs):
		"""
		Send e-mail when saving this model
		"""

		# Check if we should send this e-mail
		if not self.draft:
			emails = set()

			# Collect user e-mails
			for u in self.target_user.all():
				emails.add( u.email )

			# Get all users from campaigns
			for c in PiggyUser.objects.filter( campaignusercredit__campaign=self.target_campaign.all() ):
				emails.add( u.email )

			# Get all users from projects
			for c in PiggyUser.objects.filter( projectuserrole__project=self.target_project.all() ):
				emails.add( u.email )

			# Send custom e-mail
			send_custom_email(
				list(emails),
				self.subject,
				self.body
				)

			# Mark date sent
			self.sent_date = timezone.now()

		# Call super class
		return super(ManualEmail, self).save( *args, **kwargs )

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
			for slot in CreditSlot.objects.filter( ~Q(expireTime=0),  expireTime__gt = int(time.time()) ):

				# Discard slot
				credits.discard_slot( slot, 'expired' )

				# Delete slot
				slot.delete()
