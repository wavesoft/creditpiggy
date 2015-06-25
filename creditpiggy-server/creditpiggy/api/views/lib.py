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
from django.views.decorators.cache import cache_page
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout

from creditpiggy.core.models import CreditSlot, ComputingUnit, new_token
from creditpiggy.core.credits import flush_machine

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import allow_cors, require_valid_user, require_website_auth, sso_update, sso_user, sso_logout_flag
from creditpiggy.api import information

##########################################
# Library API Calls
##########################################

@render_with_api(context="js.claim")
@allow_cors()
@require_website_auth()
@require_valid_user()
def claim(request, api="json"):
	"""
	Claim (link) a working unit by the current user
	"""
	# Logout user if the sso sesssion is expired
	if request.user.is_authenticated() and sso_logout_flag( request.website, request.user ):
		auth_logout( request )
		raise APIError("Your session has expired", code=203)

	# Fetch machine to pair
	if not 'vmid' in request.GET:
		raise APIError("Missing 'vmid' argument", code=400)
	vmid = request.GET['vmid']

	# Create/get user/machine pair
	(unit, created) = ComputingUnit.objects.get_or_create( uuid=vmid )

	# Check for mismatch claims
	if not created:

		# Define empty unit
		if not unit.owner:
			unit.owner=request.user

		# Check for wrong claims
		elif unit.owner != request.user:
			raise APIError("The specified worker unit is already claimed", code=203)

	# Save or update record
	unit.owner=request.user
	unit.save()

	# Flush unit's credits to the user
	flush_machine( unit )

	# We are good
	return { }

@render_with_api(context="js.release")
@allow_cors()
@require_website_auth()
@require_valid_user()
def release(request, api="json"):
	"""
	Release (unlink) a working unit by the current user
	"""
	# Logout user if the sso sesssion is expired
	if request.user.is_authenticated() and sso_logout_flag( request.website, request.user ):
		auth_logout( request )
		raise APIError("Your session has expired", code=203)

	# Fetch machine to pair
	if not 'vmid' in request.GET:
		raise APIError("Missing 'vmid' argument", code=400)
	vmid = request.GET['vmid']

	# Create/get user/machine pair
	try:
		unit = ComputingUnit.objects.get( uuid=vmid, owner=request.user )
	except ComputingUnit.DoesNotExist:
		raise APIError("The specified worker unit does not exist or is not claimed", code=203)

	# Remove owner
	unit.owner = None
	unit.save()

	# We are good
	return { }

@render_with_api(context="js.session")
@allow_cors()
@require_website_auth()
def session(request, api="json"):
	"""
	Return the current session information
	"""

	# Logout user if the sso sesssion is expired
	if request.user.is_authenticated() and sso_logout_flag( request.website, request.user ):
		auth_logout( request )
		raise APIError("Your session has expired", code=203)

	# Return session details
	return information.compile_session(request)

@render_with_api(context="js.thaw")
@allow_cors()
@require_website_auth()
def thaw(request, api="json"):
	"""
	Thaw a frozen session
	"""

	# Fetch login token
	token = None
	if 'token' in request.GET:
		# Try to get a user
		user = sso_user( request.website, request.GET['token'] )
		if not user:
			raise APIError("No such token was found", code=203)
	else:
		raise APIError("Missing 'token' argument", code=400)

	# Log-in such user
	user.backend = "django.contrib.auth.backends.ModelBackend"
	auth_login( request, user )

	# Re-issue SSO token
	sso_update( request.website, user )
	
	# Return session details
	return information.compile_session(request)
