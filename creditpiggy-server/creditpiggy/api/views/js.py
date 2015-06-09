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
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_deny

from creditpiggy.core.models import CreditSlot, ComputingUnit
from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import allow_cors

##########################################
# Javascript Library API Commands
##########################################

@xframe_options_deny
@render_with_api(context="js.session")
@allow_cors(headers=["Content-Type"])
def session(request, api="json"):
	"""
	Return the current session information
	"""

	# Allocate slot or raise APIErrors
	if not request.user.is_authenticated():
		return {
			"profile": {

			}
		}

	else:

		# Get user
		user = request.user

		# Send response
		return {
			"profile": user.profile()
		}
