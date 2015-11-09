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

import pprint

import creditpiggy.frontend.aggregate.overview as overview

from django.contrib.auth.decorators import login_required
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.cache import cache_page

from creditpiggy.api.auth import website_from_request
from creditpiggy.core.achievements import campaign_next_achievement
from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *

@cache_page(60)
@xframe_options_exempt
@render_to("embed/user_status.html")
def mystatus(request):
	"""
	Display an embed with my status
	"""

	# If user is not logged in, do not show anything
	if not request.user.is_authenticated():
		return {
			'user': None
		}

	# Check if we are members of a particular website, in this case
	# show the contribution to the active campaign
	website = website_from_request(request, whitelistPath=True)
	if website:

		# Get user overview on this website
		data = overview.user_website(request.user, website)

		# Check if we have a campaign
		d_campaign = overview.campaign_user_website(request.user, website)
		if d_campaign:

			# Override properties
			data['metrics'] = d_campaign['metrics']
			data['usermetrics'] = d_campaign['usermetrics']
			data['credits'] = d_campaign['credits']
			data['ranking'] = d_campaign['ranking']

			# Set campaign details
			data['campaign'] = d_campaign['details']

		# Include user profile
		data['user'] = request.user

		# Render
		return data
	else:

		# Otherwise return a personal overview
		data = overview.user( request.user )

		# Include user profile
		data['user'] = request.user

		return data


@cache_page(60)
@xframe_options_exempt
@render_to("embed/website_status.html")
def webstatus(request):
	"""
	Display status of a website
	"""

	# Check if we are members of a particular website, in this case
	# show the contribution to the active campaign
	website = website_from_request(request, whitelistPath=True)
	if not website:
		return {
			'website': None
		}

	# Prepare response
	data = { }
	data['website'] = website

	# Check if we have a campaign
	d_campaign = Campaign.ofWebsite(website, active=True, expired=True)
	if d_campaign.exists():

		# Get first campaign
		d_campaign = d_campaign[0]

		# Get achieved instances in the order they were achieved
		data['campaign'] = {
			'details': d_campaign,
			'past': CampaignAchievementInstance.objects.order_by('date'),
			'next': campaign_next_achievement( d_campaign ),
		}

	print repr(data)
	return data

