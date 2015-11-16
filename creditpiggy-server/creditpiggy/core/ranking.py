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

from django.conf import settings
from creditpiggy.core.redis import share_redis_connection

####################################
# Individual entity ranking
####################################

def _key_revrank( key, item_id, base=1 ):
	"""
	Return the reverse ranking of a particular key
	"""

	# Get item ranking
	redis = share_redis_connection()
	rank = redis.zrevrank(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		item_id
		)

	# If missing return None
	if rank is None:
		return None

	# Otherwise adapt to base-rank
	return rank + base

def rank_user(user, base=1):
	"""
	Get overall user ranking
	"""

	# Return user ranking
	return _key_revrank( "rank/users", user.id, base )

def rank_project(project, base=1):
	"""
	Return project ranking
	"""

	# Return project ranking
	return _key_revrank( "rank/projects", project.id, base )

def rank_user_campaign(user_campaign, base=1):
	"""
	Return user's ranking in this campaign
	"""

	# Return user ranking in the specified campaign
	return _key_revrank( "rank/campaign/%i/users" % user_campaign.campaign.id, user_campaign.user.id, base )


def rank_user_project(user_project, base=1):
	"""
	Get user ranking in this project
	"""

	# Return user ranking in the specified campaign
	return _key_revrank( "rank/project/%i/users" % user_project.project.id, user_project.user.id, base )


