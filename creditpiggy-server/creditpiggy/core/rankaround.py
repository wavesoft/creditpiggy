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
from creditpiggy.core.models import *

####################################
# Ranking around a user
####################################

def _key_rank_around( key, item, item_class, num_range=100, base=1 ):
	"""
	Return the neighborhood ranking range under the specified key
	"""

	# Get multiple items with pipeline
	redis = share_redis_connection()
	pipe = redis.pipeline()

	# Get item ranking (for selecting the range)
	pipe.zrank(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		item.id
		)

	# Get item reverse ranking (for placing user in the appropriate ranking)
	pipe.zrevrank(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		item.id
		)

	# Get two items 
	(rank, revrank) = pipe.execute()

	# If missing return None
	if (rank is None) or (revrank is None):
		return None

	# Get neighborhood bounds
	n_before = int(num_range/2)
	n_after = num_range - n_before - 1

	# Clip upper bound
	if rank - n_before < 0:
		delta = rank - n_before
		n_before += delta
		n_after += delta

	# Get user ranking with score
	scores = redis.zrange(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		rank - n_before,
		rank + n_after,
		withscores=True
		)

	# Include rank number in the score series
	i = 0
	for rank in reversed(range(revrank - n_after, revrank + n_before + 1)):
		if i >= len(scores): break
		scores[i] += (rank + base,)
		i += 1

	# Extract item IDs
	uid_score_rank = {}
	uid_list = []
	for uid, score, rank in scores:

		# Skip me from the list
		if int(uid) != item.id:
			uid_list.append( uid )

		# Update score and rank
		uid_score_rank[int(uid)] = (score, rank)

	# Feth objects of every other item
	items = []
	for item in item_class.objects.filter(id__in=uid_list):

		# Get item object, extended with score and ranking
		d = to_dict( item )
		(d['score'], d['rank']) = uid_score_rank[item.id]

		# None of these is me
		d['me'] = False
		items.append(d)

	# Now add me in the list
	d = to_dict( item )
	(d['score'], d['rank']) = uid_score_rank[item.id]
	d['me'] = True
	items.append(d)

	# Sort by score descending
	items.sort( lambda a,b: int(b['score'] * 1000000) - int(a['score'] * 1000000) )

	# Return items
	return items

def rankaround_user(user, num_range=100, base=1):
	"""
	Get ranking of the neighborhood of the specified user
	"""

	# Return ranking neighborhood of users
	return _key_rank_around( "rank/users", user, PiggyUser, num_range, base )

def rankaround_project(project, num_range=100, base=1):
	"""
	Get ranking of the neighborhood of the specified project
	"""

	# Return ranking neighborhood of projects
	return _key_rank_around( "rank/projects", project, PiggyProject, num_range, base )

def rankaround_user_campaign(user_campaign, num_range=100, base=1):
	"""
	Get ranking of the neighborhood of the specified user contribution to a campaign
	"""

	# Return ranking neighborhood of projects
	return _key_rank_around( "rank/campaign/%i/users" % user_campaign.campaign.id, user_campaign.user, PiggyUser, num_range, base )

def rankaround_user_project(user_project, num_range=100, base=1):
	"""
	Get ranking of the neighborhood of the specified user contribution to project
	"""

	# Return ranking neighborhood of projects
	return _key_rank_around( "rank/project/%i/users" % user_project.project.id, user_project.user, PiggyUser, num_range, base )

