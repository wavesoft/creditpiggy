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
from django.db import models

from creditpiggy.core.models import PiggyUser

def new_token():
	"""
	UUID Generator
	"""
	return uuid.uuid4().hex

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
