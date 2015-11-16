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

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from creditpiggy.frontend.views import context
from creditpiggy.api.auth import website_from_request

from creditpiggy.core.achievements import personal_next_achievement, campaign_next_achievement
from creditpiggy.core.decorators import render_to, cache_page_per_user
from creditpiggy.core.models import *
from creditpiggy.core.utils import VisualMetricsSum
from creditpiggy.core.leaderboard import leaderboard_users_campaign, leaderboard_user_campaign, leaderboard_user_project, leaderboard_users

def auto(request):
	"""
	Automatically redirect to website or website listing
	"""

	# Check for website, detected by ?webid=xxx
	website = website_from_request(request, whitelistPath=True)

	# Redirect accordingly
	if not website:
		return redirect(reverse("frontend.profile") )
	else:
		return redirect(reverse("frontend.website.status", kwargs={'slug': website.slug} ))

@cache_page_per_user(60)
@render_to("website.html")
def status(request, slug=""):
	"""
	Website status page
	"""

	# Lookup website based on slug
	try:
		if (slug.isdigit()):
			website = Website.objects.get(id=int(slug))
		else:
			website = Website.objects.get(slug=slug)
	except Website.DoesNotExist:

		# Render error page
		return render_to_response("error.html", context(request,
				message="Could not find the website specified!"
			))

	# Get all the website metrics
	visual_metrics = website.visual_metrics.all().order_by('-priority')
	vmetric = VisualMetricsSum( visual_metrics )
	umetric = VisualMetricsSum( visual_metrics )

	# Aggregate information from all projects
	projects = []
	achievements = []
	candidate_achievement = None
	leaderboard_scores = None
	leaderboard_title = "Leaderboard is unavailable"
	for p in website.projects.all():

		# Get project record
		project_info = to_dict(p)

		# Collect projects
		projects.append( project_info )

		# Get project achievements
		if not request.user.is_authenticated():
			achievements += p.achievementStatus(None)
		else:

			# Get user achievements in this project
			achievements += p.achievementStatus(request.user)


	# Query campaigns and pick first
	campaigns = Campaign.ofWebsite(website, active=True)
	user_campaign = None

	# Update counters according to campaign or project
	if not campaigns.exists():

		# Get project counters
		for p in website.projects.all():

			# Get user's role in this project
			if request.user.is_authenticated():
				try:
					# Get user's role
					user_role = ProjectUserRole.objects.get( user=request.user, project=p )
					# Get leaderboard scores around the specified user
					leaderboard_scores = leaderboard_user_project( user_role )
					leaderboard_title = "Users close to your project score"

					# Get a candidate achievement
					if candidate_achievement is None:
						candidate_achievement = personal_next_achievement( request.user, project=p )

					# Get user's metrics
					umetric.merge( user_role.metrics() )
				except ProjectUserRole.DoesNotExist:
					pass

			# Accumulate the counters of interesting metrics
			vmetric.merge( p.metrics() )

		# Get leaderboard scores of top users
		if leaderboard_scores is None:
			leaderboard_scores = leaderboard_users()
			leaderboard_title = "Top users"

	else:

		# Get first campaign
		c = campaigns[0]

		# Prepend campaign achievements
		achievements = c.achievementStatus(unachieved=True) + achievements

		# Get user's role in this project
		if request.user.is_authenticated():
			try:
				# Get user's role in this campaign
				user_campaign = CampaignUserCredit.objects.get( user=request.user, campaign=c )

				# Get leaderboard scores around the specified user
				leaderboard_scores = leaderboard_user_campaign( user_campaign )
				leaderboard_title = "Users close to your campaign score"
				# Get user's metrics
				umetric.merge( user_campaign.metrics() )

			except CampaignUserCredit.DoesNotExist:
				pass

		# Accumulate the counters of interesting metrics
		vmetric.merge( c.metrics() )

		# Get a candidate achievement
		if candidate_achievement is None:
			candidate_achievement = campaign_next_achievement( c )

		# Get leaderboard scores of top users
		if leaderboard_scores is None:
			leaderboard_scores = leaderboard_users_campaign( c )
			leaderboard_title = "Top users in the campaign"

	# Finalize metrics summarizers
	vmetric.finalize()
	umetric.finalize()

	# Return context
	return context(request,
			website=website,
			about_body=website.desc,
			header_background=website.header_background,
			header_foreground=website.header_foreground,
			header_image=website.header_image,
			metrics=vmetric.values(),
			usermetrics=umetric.values(),
			projects=projects,
			achievements=achievements,
			campaign=user_campaign,
			candidate_achievement=candidate_achievement,
			leaderboard_scores=leaderboard_scores,
			leaderboard_title=leaderboard_title,
		)

