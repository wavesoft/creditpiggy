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

from creditpiggy.core.models import *
from creditpiggy.core.utils import VisualMetricsSum
from creditpiggy.core.achievements import personal_next_achievement

def user(user):
	"""
	Return user's overview
	"""

	# Get user counters
	user_counters = user.metrics().counters()

	# Collect user metrics
	u_user__metrics = VisualMetricsSum( VisualMetric.objects.all() )
	u_user__metrics.merge( user_counters )
	u_user__metrics.finalize()

	# Collect all achievements
	u_user__achievements = user.achievements(unachieved=True)
	u_user__candidateAchievement = personal_next_achievement( user )

	# Return details
	return {
		'title'					: 'personal contribution',
		'metrics'				: None,
		'usermetrics'			: u_user__metrics.values(),
		'achievements'			: sorted(u_user__achievements, key=lambda a: -int(a['achieved'])),
		'candidate_achievement'	: u_user__candidateAchievement,
		'credits' 				: int(user_counters.get('credits',0)),
		'ranking' 				: user.ranking(),
		'details'				: to_dict( user ),
	}


def user_website(user, website):
	"""
	Return overview of a user on a particular website 
	"""

	# Prepare information to reply
	ans = { }

	# Get all visual metrics presentable in this website
	visual_metrics = website.visual_metrics.all().order_by('-priority')
	u_project__metrics = VisualMetricsSum( visual_metrics )
	u_project__total = VisualMetricsSum( visual_metrics )
	u_project__achievements = []
	u_project__candidateAchievement = None

	# Collect metrics and achievements from all projects
	for p in website.projects.all():

		# Get user's role in this project
		try:

			# Get user's role
			user_role = ProjectUserRole.objects.get( user=user, project=p )
			# Get user's metrics
			u_project__metrics.merge( user_role.metrics() )

		except ProjectUserRole.DoesNotExist:
			pass

		# Get user achievements in this project
		u_project__achievements += p.achievementStatus(user)

		# Get a candidate achievement
		if u_project__candidateAchievement is None:
			u_project__candidateAchievement = personal_next_achievement( user, project=p, involvesMetrics=visual_metrics )

		# Accumulate the counters of interesting metrics
		u_project__total.merge( p.metrics() )

	# Include website in the answer
	return {
		'title'					: 'contribution in website %s' % website.name,
		'metrics' 				: u_project__total.values(),
		'usermetrics' 			: u_project__metrics.values(),
		'achievements' 			: sorted(u_project__achievements, key=lambda a: a['achieved']),
		'candidate_achievement'	: u_project__candidateAchievement,
		'credits' 				: int(user.metrics().counter("credits",0)),
		'ranking' 				: user.ranking(),
		'details'				: to_dict( website ),
	}

def campaign_user_website(user, website):
	"""
	Return overview of a user on a particular campaign in a website 
	"""

	# Prepare data to reply
	visual_metrics = website.visual_metrics.all().order_by('-priority')
	u_campaign__details = None
	u_campaign__metrics = VisualMetricsSum( visual_metrics )
	u_campaign__total = VisualMetricsSum( visual_metrics )

	# Get campaigns
	campaigns = Campaign.ofWebsite(website, active=True)

	# If there is no campaign in this website, return none
	if not campaigns.exists():
		return None

	# Get user's role in this campaign
	try:

		# Get user's role
		user_role = CampaignUserCredit.objects.get( user=user, campaign=campaigns[0] )

		# Update user contribution
		u_campaign__details = user_role
		u_campaign__metrics.merge( user_role.metrics() )

	except CampaignUserCredit.DoesNotExist:
		return None

	# Accumulate total metrics for comparison
	u_campaign__total.merge( c.metrics() )

	# Include campaign details in the answer
	return {
		'title'					: 'contribution in campaign %s' % campaigns[0].name,
		'metrics' 				: u_campaign__total.values(),
		'usermetrics' 			: u_campaign__metrics.values(),
		'achievements'			: None,
		'candidate_achievement'	: None,
		'credits' 				: u_campaign__details.credits,
		'ranking' 				: u_campaign__details.ranking(),
		'details'				: to_dict( u_campaign__details ),
	}
