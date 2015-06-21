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
import uuid
from django.db import models

from creditpiggy.core.models import gen_token_key, new_uuid, new_token, PiggyUser, PiggyProject, Website

###################################################################
# Authentication Models
###################################################################

class SingleAuthLoginToken(models.Model):
	"""
	A token that can be used for token-only authentication.
	Such tokens expire after use and have to be re-issued. 
	"""

	#: Authentication token
	token = models.CharField(max_length=32, default=new_token, unique=True, db_index=True, 
		help_text="Single-use log-in token")

	#: The user
	user = models.ForeignKey( PiggyUser )

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

class WebsiteCredentials(models.Model):
	"""
	Credentials for each website
	"""

	#: Authentication token
	token = models.CharField(max_length=32, default=new_uuid, unique=True, db_index=True, 
		help_text="Anonymous authentication token for the website")

	#: The website linked to this credentials
	website = models.ForeignKey( Website )

	#: A list of valid domains
	domains = models.TextField(default="[]")

	# Check if domain is authenticated
	def hasDomain(self, domainName):
		"""
		Check if the specified domain is registered in the list of authenticated domains
		"""

		# Load domains
		domains = json.loads(self.domains)
		return domainName.lower() in domains

	def getDomains(self):
		"""
		Return a list of all domains
		"""
		return json.loads(self.domains)

