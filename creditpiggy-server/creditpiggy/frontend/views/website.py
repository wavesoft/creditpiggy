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

from creditpiggy.core.achievements import personal_next_achievement
from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *
from creditpiggy.core.utils import VisualMetricsSum

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

			# Get a candidate achievement
			if candidate_achievement is None:
				candidate_achievement = personal_next_achievement( request.user, project=p )


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
					# Get user's metrics
					umetric.merge( user_role.metrics() )
				except ProjectUserRole.DoesNotExist:
					pass

			# Accumulate the counters of interesting metrics
			vmetric.merge( p.metrics() )

	else:

		# Get campaign counters
		for c in campaigns:

			# Get user's role in this project
			if request.user.is_authenticated():
				try:
					# Get user's role
					user_role = CampaignUserCredit.objects.get( user=request.user, campaign=c )
					# Keep user's campaign
					user_campaign = user_role
					# Get user's metrics
					umetric.merge( user_role.metrics() )
				except CampaignUserCredit.DoesNotExist:
					pass

			# Accumulate the counters of interesting metrics
			vmetric.merge( c.metrics() )

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
		)

