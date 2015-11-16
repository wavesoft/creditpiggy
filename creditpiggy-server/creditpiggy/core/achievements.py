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

import time
import random
import logging

from django.db.models import Q
from creditpiggy.core.utils.metrics import VisualMetrics
from creditpiggy.core.models import Achievement, AchievementInstance, PersonalAchievement, CampaignAchievementInstance, CampaignUserCredit, VisualMetric
from creditpiggy.core.email import send_project_achievement_email, send_personal_achievement_email, send_campaign_achievement_email

################################################
# 
################################################

def shortlist_candidates( candidates, counters, valid_metrics=None, pick_one=True ):
	"""
	Shortlist candidate achievements
	"""

	# Iterate over the candidates and calculate the
	# distance from the user's current counters
	candidate_dist = None
	candidate_shortlist = None
	for c in candidates:
		distance = 1.0
		metric = c.getMetrics()

		# Discard invalid candidates
		if not valid_metrics is None:
			discard = False
			for k,v in metric.iteritems():
				if not k in valid_metrics:
					discard = True
					break
			# If we should discard this, continue
			if discard:
				continue

		# Calculate distance to all metrics
		for k,v in metric.iteritems():

			# Get user value
			val_user = 0.0
			if k in counters:
				val_user = float(counters[k])

			# Contribute to distance
			distance *= val_user / v

		# Pick candidate
		if (candidate_dist is None) or (distance >= candidate_dist):

			# Check if we should clear shortlist
			if (distance > candidate_dist):
				candidate_shortlist = []

			# Update current metrics
			candidate_dist = distance

			# Include in short list
			candidate_shortlist.append( (c, metric) )

	# Return none if no candidate
	if not candidate_shortlist:
		return (None, None)

	# Return shortlist or one item
	if pick_one:
		return random.choice( candidate_shortlist )
	else:
		return candidate_shortlist


################################################
# Interface functions
################################################

def campaign_next_achievement( campaign ):
	"""
	Return the next candidate achievement for the specified campaign
	"""

	# Get all user's counters
	counters = campaign.metrics().counters()

	# Get all un-achieved achievements
	candidates = campaign.achievements.exclude(campaignachievementinstance__campaign=campaign)

	# Shortlist and pick candidate
	(candidate, candidate_metrics) = shortlist_candidates( candidates, counters, pick_one=True )
	if not candidate:
		return None

	# Get Visual Metrics translator
	vm = VisualMetrics( VisualMetric.objects.filter( name__in=candidate_metrics.keys() ) )

	# Format reference visual metric values 
	metrics_with_scale = vm.format( candidate_metrics )

	# Calculate scale
	for k,v in metrics_with_scale.iteritems():

		# Get user value
		val_user = 0.0
		if k in counters:
			val_user = float(counters[k])

		# Add additional metadata
		v['progress'] = val_user * 100.0 / v['value']
		v['diff'] = v['value'] - val_user
		v['diff_text'] = vm.getDisplayValue( k, v['diff'] )

	# Return candidate description
	return {
		'achievement': candidate,
		'metrics': metrics_with_scale.values(),
	}

def personal_next_achievement( user, project=None, involvesMetrics=None ):
	"""
	Return next candidate personal achievement for the specified user
	"""

	# Get all user's counters
	counters = user.metrics().counters()

	# Get all un-achieved achievements
	if project is None:
		candidates = Achievement.objects.exclude(achievementinstance__user=user)
	else:
		candidates = project.achievements.exclude(achievementinstance__user=user)

	# Populate valid_metrics if we are invovling metrics
	valid_metrics = None
	if not involvesMetrics is None:
		valid_metrics = []
		for m in involvesMetrics:

			# Get metric name (we accept array of strings or array of VisualMetrics)
			m_name = m
			if isinstance(m, str) or isinstance(m, unicode):
				m_name = m
			elif isinstance(m, VisualMetric):
				m_name = m.name

			# Collect valid metric
			valid_metrics.append( m_name )

	# Shortlist and pick candidate
	(candidate, candidate_metrics) = shortlist_candidates( candidates, counters, valid_metrics=valid_metrics, pick_one=True )
	if not candidate:
		return None

	# Get Visual Metrics translator
	vm = VisualMetrics( VisualMetric.objects.filter( name__in=candidate_metrics.keys() ) )

	# Format reference visual metric values 
	metrics_with_scale = vm.format( candidate_metrics )

	# Calculate scale
	for k,v in metrics_with_scale.iteritems():

		# Get user value
		val_user = 0.0
		if k in counters:
			val_user = float(counters[k])

		# Add additional metadata
		v['progress'] = val_user * 100.0 / v['value']
		v['diff'] = v['value'] - val_user
		v['diff_text'] = vm.getDisplayValue( k, v['diff'] )

	# Return candidate description
	return {
		'achievement': candidate,
		'metrics': metrics_with_scale.values(),
	}

def metrics_achieved( counters, achievement_metrics ):
	"""
	Check if user counters are compatible for awarding the
	achievement, defined by the achievement_metrics.
	"""

	# Iterate over achievement metrics
	for k,v in achievement_metrics.iteritems():
		# No key in counters? Next ..
		if not k in counters:
			return False
		# If counters are not achieved, continue
		try:
			# Float comparison that covers also int cases
			if float(counters[k]) < float(v):
				return False
		except ValueError:
			print "ValueError while parsing counters[%k]=%r < %r" % (k, counters[k], v)
			return False

	# Matched
	return True

def check_campaign_achievements( campaign ):
	"""
	Check the campaign's achievements
	"""

	# Get campaign-achievement link metrics
	metrics = campaign.metrics()
	m_counters = metrics.counters()

	# Iterate over non-achieved achievements in the campaign instances
	for a in campaign.achievements.exclude( campaignachievementinstance__campaign=campaign ):

		# For each achievement, check if metrics are achieved
		if metrics_achieved( m_counters, a.getMetrics() ):

			# Award the achievement to the campaign
			ac = CampaignAchievementInstance(
					campaign=campaign,
					achievement=a
				)
			ac.save()

			# If this achievement should be awarded to all members
			# of the campaign, perform mass award now
			if a.team:

				# Collect all users
				users = []
				for cuc in CampaignUserCredit.objects.filter( campaign=campaign, user__email_achievement=True ):
					users.append( cuc.user )

				# Send to all of them
				send_campaign_achievement_email( users, ac )

def check_personal_achievements( user ):
	"""
	Check the user's personal achievements
	"""

	# Get user-achievement link metrics
	metrics = user.metrics()
	m_counters = metrics.counters()

	# Get non-achieved personal achievements
	for a in Achievement.objects.filter(personal=True).exclude( personalachievement__user=user ):

		# For each achievement, check if metrics are achieved
		if metrics_achieved( m_counters, a.getMetrics() ):

			# Award the achievement to the user
			ac = PersonalAchievement(
					user=user,
					achievement=a,
				)
			ac.save()

			# Send e-mail
			send_personal_achievement_email( user, ac )

def check_achievements( project_user_link ):
	"""
	Check the user achievements
	"""

	# Get user-achievement link metrics
	metrics = project_user_link.metrics()
	m_counters = metrics.counters()

	# Get non-achieved project achievements
	for a in project_user_link.project.achievements.exclude( achievementinstance__user=project_user_link.user, achievementinstance__project=project_user_link.project ):

		# For each achievement, check if metrics are achieved
		if metrics_achieved( m_counters, a.getMetrics() ):

			# Award the achievement to the user
			ac = AchievementInstance(
					user=project_user_link.user,
					project=project_user_link.project,
					achievement=a,
					campaign=None,
				)
			ac.save()

			# Send e-mail
			send_project_achievement_email( project_user_link, ac )

