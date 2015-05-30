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

import random
import time
from django.db import models
#from creditpiggy.frontend.models import PiggyUser, Project, ProjectRevision

# def gen_token_key():
# 	"""
# 	Token key generator
# 	"""
# 	# Token charset
# 	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
# 	key = ""
# 	for i in range(0, 32):
# 		key += charset[random.randint(0, len(charset)-1)]

# 	# Return a unique key
# 	return key

# def gen_token_salt():
# 	"""
# 	Token salt generator
# 	"""
# 	# Salt charset
# 	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZ+abcdefghijklmnopqrstuvwxyz-0123456789~!@#$%^&*(){}[]<>,./?;:'\"\\|`"
# 	key = ""
# 	for i in range(0, 64):
# 		key += charset[random.randint(0, len(charset)-1)]

# 	# Return a unique key
# 	return key

# class AuthToken(models.Model):
# 	"""
# 	Authenticataion tokens
# 	"""

# 	USER = 'US'
# 	DEVELOPER = 'DE'
# 	SERVICE = 'SV'
# 	TOKEN_TYPE = (
# 		(USER, 'User'),
# 		(DEVELOPER, 'Devleoper'),
# 		(SERVICE, 'Service'),
# 	)

# 	# Owner of this authentication token
# 	user = models.ForeignKey(PiggyUser)

# 	# Authentication key
# 	auth_key = models.CharField(max_length=64, default=gen_token_key, db_index=True, help_text="A unique ID used by server-side software to identify the user")
# 	auth_salt = models.CharField(max_length=64, default=gen_token_salt, help_text="The salt for authenticaton checksum token")
# 	auth_hash = models.CharField(max_length=256, verbose_name="Secret", help_text="A validation checksum hash for the secret key in the user's computer")

# 	# Authentication token type
# 	tokenType = models.CharField(max_length=2, choices=TOKEN_TYPE, default=USER)

# 	def __unicode__(self):
# 		return "%s (%s)" % (self.user, self.auth_key)

# class ProjectAuthToken(models.Model):
# 	"""
# 	Project-wide authentication tokens
# 	"""

# 	USER = 'US'
# 	DEVELOPER = 'DE'
# 	SERVICE = 'SV'
# 	TOKEN_TYPE = (
# 		(USER, 'User'),
# 		(DEVELOPER, 'Devleoper'),
# 		(SERVICE, 'Service'),
# 	)

# 	token = models.ForeignKey(AuthToken)
# 	project = models.ForeignKey(Project)

# 	# Authentication token type
# 	tokenType = models.CharField(max_length=2, choices=TOKEN_TYPE, default=USER)

# 	def __unicode__(self):
# 		return "%s (%s)" % (self.token.user, self.token.auth_key)

# class CreditCache(models.Model):
# 	"""
# 	Intermediate (cache) table where credits are placed
# 	before later processed by the credit arachiving and evaluation process.
# 	"""

# 	# Reference
# 	user = models.ForeignKey(PiggyUser)
# 	project = models.ForeignKey(ProjectRevision)

# 	# Credit value
# 	credit = models.IntegerField()

# class CreditSlot(models.Model):
# 	"""
# 	A credit slot is allocated by a project server and consumed by a client
# 	"""
