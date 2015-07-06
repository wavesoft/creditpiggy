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

import json
import time
import logging

from django.db import models
from django.conf import settings

from creditpiggy.core.redis import share_redis_connection
from creditpiggy.core.housekeeping import HousekeepingTask, periodical
from creditpiggy.core.models import *

# Get housekeeping logger
logger = logging.getLogger(__name__)

############################################################
# Project-level normalization
############################################################

class ProjectNormalizer(HousekeepingTask):
	"""
	This project normalization class is responsible for calculating
	the normalization factor for each project.

	This factor will be used to gauge the user project and the user ranking
	in the global scale.
	"""

	def __init__(self):
		"""
		Open a REDIS connection
		"""

		# Open a redis connection
		self.redis = share_redis_connection()

	def update_user_ranking(self):
		"""
		Update user ranking
		"""

		# Index of users
		score_index = { }

		# Get all users participating in this project
		for u in ProjectUserRole.objects.all():

			# Make sure we have a key
			if not u.user.id in score_index:
				score_index[ u.user.id ] = 0

			# Collect normalization credits
			score_index[ u.user.id ] += u.norm_credits

		# Create a transaction for REDIS operations
		pipe = self.redis.pipeline()

		# Update user ranking
		for u, score in score_index.iteritems():

			logger.debug("Updated user #%i credits to: %i" % (u, score))

			# Update user ranking
			pipe.zadd(
				"%srank/users" % (settings.REDIS_KEYS_PREFIX,),
				score, u 
				)

		# Run pipeline
		pipe.execute()

	def normalize_project_users(self, project):
		"""
		Normalize the credits of all users
		"""

		# Create a transaction for REDIS operations
		pipe = self.redis.pipeline()

		# Count project credits to update project ranking
		project_credits = 0

		# Get all users participating in this project
		for u in ProjectUserRole.objects.filter(project=project):

			# Calculate normalized project credits
			norm_credits = u.credits / project.norm_factor

			# Update user record
			if norm_credits != u.norm_credits:
				u.norm_credits = norm_credits
				u.save()

			# Calculate project credits
			project_credits += norm_credits

			# Store normalized credits
			logger.debug("Updated user #%i contribution to project '%s': %i" % (u.user.id, str(u.project), norm_credits))
			pipe.zadd(
				"%srank/project/%i/users" % (settings.REDIS_KEYS_PREFIX, project.id), 
				norm_credits, u.user.id
			)

		# Store normalized credits
		logger.debug("Updated project '%s' credits to: %i" % (str(project), project_credits))
		pipe.zadd(
			"%srank/projects" % (settings.REDIS_KEYS_PREFIX,), 
			project_credits, project.id
		)

		# Run pipeline
		pipe.execute()

	@periodical(minutes=30)
	def normalize_projects(self):
		"""
		Normalize all projects
		"""

		# Reset projects
		self.projects = {}
		
		# Load credit distributions from all projects
		for p in PiggyProject.objects.all():

			# Get distribution of credits
			histo = p.metrics().histogram("credits")

			# If we don't have data, assume '1.0'
			norm = 1.0
			if histo:

				logger.debug("Project '%s' distribution: %r" % ( str(p), histo ))

				# Perform weighted summarization using the
				# number of samples on the particular credit 
				# slot as the weight.
				num = 0.0
				denom = 0.0
				for k,v in histo.iteritems():
					num += float(k) * float(v)
					denom += float(v)

				# Calculate weighted average
				if denom != 0:
					norm = num / denom

			logger.info("Project '%s' normalization factor: %f" % ( str(p), norm ))

			# Apply project's normalization factor
			if p.norm_factor != norm:
				p.norm_factor = norm
				p.save()

			# Update user normalization on this project
			self.normalize_project_users( p )

		# Update user credits
		self.update_user_ranking()
