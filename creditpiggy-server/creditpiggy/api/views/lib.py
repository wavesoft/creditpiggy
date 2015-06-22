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

from creditpiggy.core.models import CreditSlot, ComputingUnit
from creditpiggy.api.models import SingleAuthLoginToken, new_token

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import allow_cors, require_valid_user, require_website_auth
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
	return { }

@render_with_api(context="js.release")
@allow_cors()
@require_website_auth()
@require_valid_user()
def release(request, api="json"):
	"""
	Release (unlink) a working unit by the current user
	"""
	return { }

@render_with_api(context="js.handshake")
@allow_cors()
@require_website_auth()
def handshake(request, api="json"):
	"""
	Initial handshake between the javascript library and the server
	"""
	return { }

@render_with_api(context="js.session")
@allow_cors()
@require_website_auth()
def session(request, api="json"):
	"""
	Return the current session information
	"""
	
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
		try:
			token = SingleAuthLoginToken.objects.get( token=request.GET['token'] )
		except SingleAuthLoginToken.DoesNotExist:
			raise APIError("No such token was found", code=203)
	else:
		raise APIError("Missing 'token' argument")

	# Log-in such user
	token.user.backend = "django.contrib.auth.backends.ModelBackend"
	auth_login( request, token.user )

	# Consume
	token.delete()
	
	# Return session details
	return information.compile_session(request)

@render_with_api(context="js.poll")
@allow_cors()
@require_website_auth()
@cache_page(30)
def poll(request, api="json"):
	"""
	Respond polling information that might be pending for the 
	current user.
	"""

	# Prepare polling information
	info = { }

	# Allocate slot or raise APIErrors
	if request.user.is_authenticated():
		info = { }

	# Define interval for polling
	info['interval'] = 30

	# Return message
	return info
