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

from django.db import models
from django.conf import settings

from creditpiggy.core.redis import share_redis_connection
from creditpiggy.core.housekeeping import HousekeepingTask, periodical
from creditpiggy.core.models import *

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

	def normalize_users(self):
		"""
		Normalize the credits of all users
		"""

		# Get all projects to iterate upon
		projects = PiggyProject.objects.all()[:]

		# Get all users
		for u in PiggyUser.objects.all():

			# 

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
			histo = p.histogram("credits")

			# If we don't have data, assume '1.0'
			norm = 1.0
			if histo:

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

			# Apply project's normalization factor
			if p.norm_factor != norm:
				p.norm_factor = norm
				p.save()

		# Update user normalization
		self.normalize_users()


############################################################
# User-level normalization
############################################################

def update_user_ranking( user ):
	"""
	Re-calculate the user's ranking
	"""


