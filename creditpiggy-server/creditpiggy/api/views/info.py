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

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone

from creditpiggy.core.models import *
from creditpiggy.core.credits import import_machine_slots
from creditpiggy.core.achievements import check_personal_achievements
from creditpiggy.core.utils import VisualMetricsSum

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import allow_cors, website_from_request

##########################################
# Information Calls
##########################################

@render_with_api(context="js.website_info")
@allow_cors()
def website(request, api="json"):
	"""
	Query details regarding a website
	"""

	# Get website details
	website = website_from_request( request, whitelistPath=True )
	if not website:
		raise APIError("I don't know what's the website you are querying for!")

	# Get website visual metrics
	visual_metrics = website.visual_metrics.all().order_by('-priority')
	vmetric = VisualMetricsSum( visual_metrics )

	# Query campaigns and pick first
	campaigns = Campaign.ofWebsite(website, active=True)
	if campaigns.exists():

		# Pick first campaign
		campaign = campaigns[0]

		# Get counters
		vmetric.merge( campaign.metrics() )
		vmetric.finalize()

		# Render
		return {
			"campaign": {
				"name": campaign.name,
				"started": str(campaign.start_time),
				"ending": str(campaign.end_time),
				"remaining": (campaign.end_time - timezone.now()).seconds,
			},
			"website": {
				"name": website.name,
				"short": website.short,
				"url": website.url,
				"icon": website.icon,
				"header_foreground": website.header_foreground,
				"header_background": website.header_background,
				"header_image": website.header_image,
			},
			"counters": vmetric,
		}

	else:

		# Get project counters
		for p in website.projects.all():
			vmetric.merge( p.metrics() )
		vmetric.finalize()

		# Render
		return {
			"campaign": None,
			"website": {
				"name": website.name,
				"short": website.short,
				"url": website.url,
				"icon": website.icon,
				"header_foreground": website.header_foreground,
				"header_background": website.header_background,
				"header_image": website.header_image,
			},
			"counters": vmetric,
		}

