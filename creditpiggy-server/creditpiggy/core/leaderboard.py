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

"""

from creditpiggy.core.leaderboard import *
from creditpiggy.core.models import *
u = PiggyProject.objects.all()[0]
leaderboard_project(u)

"""

####################################
# Leaderboard functions
####################################

def _objectify_ranking( scores, item_class, item=None ):
	"""
	Create model objects representing the items in the score list specified

	NOTE: This fucntion requires the enriched version of scores list, using
	      the tuple format: (uid, score, rank)
	"""

	# Extract item IDs
	uid_score_rank = {}
	uid_list = []
	for uid, score, rank in scores:

		# Skip me from the list
		if (item is None) or (int(uid) != item.id):
			uid_list.append( uid )

		# Update score and rank
		uid_score_rank[int(uid)] = (score, rank)

	# Feth objects of every other item
	items = []
	for i in item_class.objects.filter(id__in=uid_list):

		# Get item object, extended with score and ranking
		d = to_dict( i )
		(d['score'], d['rank']) = uid_score_rank[i.id]

		# None of these is me
		d['me'] = False
		items.append(d)

	# Now add the pivot item in the list
	if not item is None:
		d = to_dict( item )
		(d['score'], d['rank']) = uid_score_rank[item.id]
		d['me'] = True
		items.append(d)

	# Sort by score descending
	items.sort( lambda a,b: int(b['score'] * 1000000) - int(a['score'] * 1000000) )

	# Return items
	return items

def _key_rank_around( key, item, item_class, num_range=100, base=1 ):
	"""
	Return the neighborhood ranking range under the specified key
	"""

	# Get multiple items with pipeline
	redis = share_redis_connection()
	revrank = redis.zrevrank(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		item.id
		)

	# If missing return None
	if revrank is None:
		return None

	# Get neighborhood bounds
	n_before = int(num_range/2)
	n_after = num_range - n_before - 1

	# Clip upper bound
	if (revrank - n_before) < 0:
		delta = n_before- revrank
		n_before -= delta
		n_after += delta

	# Get user ranking with score
	scores = redis.zrevrange(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		revrank - n_before,
		revrank + n_after,
		withscores=True
		)

	# Enrich with ranking index
	ranks = range( revrank - n_before, revrank + n_after + 1 )
	scores = [ scores[i] + (ranks[i] + base,) for i in range(0,len(scores)) ]

	# Create objects from the rank IDs
	return _objectify_ranking( scores, item_class, item )

def _key_rank_top( key, item_class, num_range=100, base=1 ):
	"""
	Return the first num_range items from the specified rank-ordered list
	"""

	# Return a range of items
	redis = share_redis_connection()
	scores = redis.zrevrange(
		"%s%s" % (settings.REDIS_KEYS_PREFIX, key),
		0,
		num_range - 1,
		withscores=True,
		)

	# If scores is empty or None, return None
	if not scores:
		return None

	# Enrich with ranking index
	ranks = range(0, num_range)
	scores = [ scores[i] + (ranks[i] + base,) for i in range(0,len(scores)) ]

	# Objectify
	return _objectify_ranking( scores, item_class )


####################################
# Per entity details
####################################

def leaderboard_user(user, num_range=100, base=1):
	"""
	Get leaderboard of the specified user
	"""

	# Return leaderboard neighborhood of users
	return _key_rank_around( "rank/users", user, PiggyUser, num_range, base )

def leaderboard_project(project, num_range=100, base=1):
	"""
	Get leaderboard of the specified project
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_around( "rank/projects", project, PiggyProject, num_range, base )

def leaderboard_user_campaign(user_campaign, num_range=100, base=1):
	"""
	Get leaderboard of the specified user's contribution to a campaign
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_around( "rank/campaign/%i/users" % user_campaign.campaign.id, user_campaign.user, PiggyUser, num_range, base )

def leaderboard_user_project(user_project, num_range=100, base=1):
	"""
	Get leaderboard of the specified user's contribution to project
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_around( "rank/project/%i/users" % user_project.project.id, user_project.user, PiggyUser, num_range, base )


####################################
# Overall details 
####################################

def leaderboard_users(num_range=100, base=1):
	"""
	Get leaderboard of top users
	"""

	# Return leaderboard neighborhood of users
	return _key_rank_top( "rank/users", PiggyUser, num_range, base )

def leaderboard_projects(num_range=100, base=1):
	"""
	Get leaderboard of top projects
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_top( "rank/projects", PiggyProject, num_range, base )

def leaderboard_users_campaign(campaign, num_range=100, base=1):
	"""
	Get leaderboard of top user's contribution to a campaign
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_top( "rank/campaign/%i/users" % campaign.id, PiggyUser, num_range, base )

def leaderboard_users_project(project, num_range=100, base=1):
	"""
	Get leaderboard of top user's contribution to project
	"""

	# Return leaderboard neighborhood of projects
	return _key_rank_top( "rank/project/%i/users" % project.id, PiggyUser, num_range, base )

####################################
# Merge various leaderboard values 
####################################

def merge_leaderboards(leaderboards):
	"""
	Merge individual leaderboard result
	"""
	pass
