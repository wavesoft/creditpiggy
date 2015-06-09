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

from django.db.models import Q
from creditpiggy.core.models import Achievement, AchievementInstance

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
		if counters[k] < v:
			return False

	# Matched
	return True


def check_achievements( project_user_link ):
	"""
	Check the user achievements
	"""

	# Get user-achievement link metrics
	metrics = project_user_link.metrics()
	m_counters = metrics.counters()

	# # Get user's achievements for this project
	# user_achievements = []
	# for a in AwardedUserProjectAchievement.objects.filter( user=project_user_link.user ):
	# 	user_achievements.append(a)

	# # Get relevant project achievements
	# for a in ProjectAchievement.objects.filter( ~Q(achievement__in=user_achievements), project=project_user_link.project ):

	# 	# For each achievement, check if metrics are achieved
	# 	if metrics_achieved( m_counters, a.getMetrics() ):

	# 		# Award the achievement to the user
	# 		ac = AwardedUserProjectAchievement(
	# 				user=project_user_link.user,
	# 				award=a,
	# 				achieved_at=time.time(),
	# 			)
	# 		ac.save()


