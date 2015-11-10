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

from django.views.decorators.cache import cache_page
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from creditpiggy.frontend.views import context
from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *

# @cache_page( 25200 ) # A week
@render_to("share/achievement.html")
def achievement(request, aid):
	"""
	Share an achievement
	"""

	# Get achievement from id
	achievement = achievement_from_share_id( aid )
	if achievement is None:
		return redirect(reverse("frontend.home") )

	# Try to lookup a relevant campaign
	campaign = None
	project = None
	see_more_link = ""
	see_more_title = ""
	if isinstance( achievement, CampaignAchievementInstance ):

		# Link to website
		see_more_link = reverse("frontend.website.status", kwargs={'slug': achievement.campaign.website.slug} )
		see_more_title = achievement.campaign.website.name

		# Get related campaign
		campaign = achievement.campaign

		# If we have a url, update see more link
		if achievement.campaign.website.url:
			see_more_link = achievement.campaign.website.url

	elif isinstance( achievement, AchievementInstance ):

		# Get related project
		project = achievement.project

		# Get websites hosting this project
		websites = Website.objects.filter(projects=achievement.project)
		if websites.exists():
			see_more_link = reverse("frontend.website.status", kwargs={'slug': websites[0].slug} )
			see_more_title = websites[0].name

			# If we have a url, update see more link
			if websites[0].url:
				see_more_link = websites[0].url

	# If we have a see more link, add tracking code
	if see_more_link and request.user.is_authenticated():
		see_more_link += "?cpr=%s." % request.user.getRefererID()

	# Return context
	return context(request,
		achievement=achievement,
		campaign=campaign,
		project=project,
		see_more=see_more_link,
		see_more_title=see_more_title,
		)

