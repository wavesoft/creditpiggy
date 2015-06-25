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

import hashlib
import re

from functools import wraps
from urlparse import urlparse

from django.http import HttpResponse
from django.conf import settings

from creditpiggy.core.redis import share_redis_connection
from creditpiggy.api.protocol import APIError
from creditpiggy.api.models import ProjectCredentials, WebsiteCredentials, new_token
from creditpiggy.core.models import Website, PiggyUser

###############################################################
# Private methods
###############################################################

def _validate_project_auth( payload, auth ):
	"""
	Validate the checksum of the payload using the credentials specified and
	return the project they are associated with.
	"""

	# Split autentication parameter
	auth_parts = auth.lower().split(",")
	if len(auth_parts) != 3:
		raise APIError("Your authentication token is malformed", code=400)

	# get the digest algoritm used
	(algo, token, vdigest) = auth_parts

	# Lookup project
	try:
		cred = ProjectCredentials.objects.get(token=token)
	except ProjectCredentials.DoesNotExist:
		return None

	# Hash data using hash function
	if algo == "sha-256":
		digest = hashlib.sha256(payload + cred.secret).hexdigest()
	elif algo == "sha-512":
		digest = hashlib.sha512(payload + cred.secret).hexdigest()
	elif algo == "sha-1":
		digest = hashlib.sha1(payload + cred.secret).hexdigest()
	else:
		raise APIError("Unknown hashing algorithm used", code=400)

	print ">>> Payload: '%s' (%s='%s')" % (payload, algo, digest)
	print ">>> Auth: '%s'" % auth
	print ">>> V-Digest: '%s'" % vdigest

	# Return project if digest is validated
	if digest == vdigest:
		return cred.project
	else:
		return None

###############################################################
# Utility functions
###############################################################

def website_from_request(request, whitelistPath=[]):
	"""
	Locate the website from the specified request
	"""

	# If it's already cached, fetch it directly
	if hasattr(request, 'website'):
		return request.website

	# If we are from a project website, get the web ID
	if hasattr(request, 'webid'):

		# Lookup website from webid
		try:
			cred = WebsiteCredentials.objects.get( token=request.webid )
		except WebsiteCredentials.DoesNotExist:
			return None

		# Check if we are in a whitelist path
		skipCheck = False
		if whitelistPath == True:
			skipCheck = True
		else:
			for wl in whitelistPath:
				if re.match( wl, request.path ):
					skipCheck = True
					break

		# If we should not skip checks, check domain
		if not skipCheck:

			# Parse referer header
			referer = request.META.get('HTTP_REFERER', None)
			if not referer:
				return None

			# Skip internal domain(s)
			if not referer in settings.ALLOWED_HOSTS:

				# Validate external domain
				url = urlparse(referer)
				if not cred.hasDomain( url.netloc ):
					return None

		# Return website
		return cred.website

def sso_update(website, user, issue=False):
	"""
	Update the singe-sign-on token for the specified user
	for the specified website.
	"""

	# Open a redis connection
	redis = share_redis_connection()
	# Update SSO token for this user
	key = "%sssotoken" % settings.REDIS_KEYS_PREFIX

	# New unique ID of token
	token = new_token()

	# Token to user (token -> user)
	tu_key = "%i:t:%s" % (website.id, token)
	# User to token (user -> token)
	ut_key = "%i:u:%i" % (website.id, user.id)
	# Logout flag
	lo_key = "%i:%i:logout" % (website.id, user.id)

	# Delete user's previous token-to-user key
	tok = redis.hget( key, ut_key )
	if tok:
		redis.hdel( key, tok )
	else:
		# There was no previous token, so if we were
		# not told to issue a new one, return None
		if not issue:
			return None

	# Update current token
	keys = {}
	keys[ut_key] = tu_key	# User -> to Token key
	keys[tu_key] = user.id 	# Token -> to User
	redis.hmset( key, keys )

	# Delete logout flag
	redis.hdel( key, lo_key )	

	# Return token
	return token

def sso_logout_flag( website, user ):
	"""
	Check if user logged out from the specified sso session.
	"""

	# Open a redis connection
	redis = share_redis_connection()
	# Update SSO token for this user
	key = "%sssotoken" % settings.REDIS_KEYS_PREFIX

	# Check for logout key
	lo_key = "%i:%i:logout" % (website.id, user.id)
	tok = redis.hget( key, lo_key )
	return bool(tok)

def sso_logout(user, website=None):
	"""
	Log-out from the specified singe-sign-on context.
	If website is not specified, the user is logged out from all websites
	"""

	# Open a redis connection
	redis = share_redis_connection()
	# Update SSO token for this user
	key = "%sssotoken" % settings.REDIS_KEYS_PREFIX

	# Convert 'website' to an interable array
	if website is None:
		website = Website.objects.all()
	elif not isinstance(website, list) and not isinstance(website, tuple):
		website = [ website ]

	# Loop over websites and expire tokens
	for w in website:

		# Delete user's previous token-to-user & user-to-token keys
		ut_key = "%i:u:%i" % (w.id, user.id)
		tok = redis.hget( key, ut_key )
		if tok:
			redis.hdel( key, tok )
			redis.hdel( key, ut_key )

		# Create logout token
		lo_key = "%i:%i:logout" % (w.id, user.id)
		redis.hset( key, lo_key, 1 )	

def sso_get(website, user):
	"""
	Return the current SSO token for the specified website/user combination.
	"""

	# Open a redis connection
	redis = share_redis_connection()
	# Update SSO token for this user
	key = "%sssotoken" % settings.REDIS_KEYS_PREFIX

	# Locate the user-to-token key in order to 
	# extract the SSO token
	ut_key = "%i:u:%i" % (website.id, user.id)
	tok = redis.hget( key, ut_key )
	if tok:

		# Return the token part of the key
		parts = tok.split(":")
		return parts[2]

	# Otherwise, return None
	return None

def sso_user(website, token):
	"""
	Return the user that owns the specified token
	"""

	# Open a redis connection
	redis = share_redis_connection()
	# Update SSO token for this user
	key = "%sssotoken" % settings.REDIS_KEYS_PREFIX

	# Locate the token-to-user key and fetch it's contents
	tu_key = "%i:t:%s" % (website.id, token)
	usr = redis.hget( key, tu_key )
	if usr:
		# Return the user
		try:
			return PiggyUser.objects.get(id=int(usr))
		except PiggyUser.DoesNotExist:
			return None

	# Otherwise, return None
	return None

###############################################################
# Decorators
###############################################################

def throttle(rate=None, span=None):
	"""
	Throttle the incoming requests to the specified [rate] per [span] seconds
	"""
	pass

def allow_cors( origin="*", headers="*" ):
	"""
	Add the cross-origin request header in the response.

	@decorator
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):

			# Compile headers to string
			if isinstance(headers, list) or isinstance(headers, tuple):
				hdr = ", ".join(headers)
			else:
				hdr = str(headers)

			# If we have protocol in the request, use that channel for specifying headers
			if hasattr(request, 'proto'):
				request.proto.add_header('Access-Control-Allow-Origin', origin)
				request.proto.add_header('Access-Control-Allow-Headers', hdr)
				return func(request, *args, **kwargs)

			# Otherwise wait for response and then append the header there
			else:
				res = func(request, *args, **kwargs)
				if isinstance(res, HttpResponse):
					res['Access-Control-Allow-Origin'] = origin
					res['Access-Control-Allow-Headers'] = hdr
				return res

		return wrapper
	return decorator

def require_valid_user():
	"""
	Demand a valid user before continuing with the wrapped function.

	@decorator
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):

			# Require a user header to be preent
			if not request.user.is_authenticated():
				raise APIError("You must be logged in to use this resource", code=401)

			# Run function
			return func(request, *args, **kwargs)

		return wrapper
	return decorator

def require_website_auth():
	"""
	Demand a valid website authentication credentials to be present
	in the request parameters.

	@decorator
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, api="json", *args, **kwargs):

			# Raise syntax error if 'proto' does not exist in header
			if not hasattr(request, 'proto'):
				raise SyntaxError("The 'require_website_auth' decorator requires a 'render_with_api' decorator first!")

			# Parse referer header
			referer = request.META.get('HTTP_REFERER', '')
			url = urlparse(referer)

			# Lookup authentication token
			token = request.proto.get('webid', required=True)

			# Lookup an API token
			try:
				cred = WebsiteCredentials.objects.get( token=token )
			except WebsiteCredentials.DoesNotExist:
				raise APIError("You are not authorized to use this resource", code=401)

			# Validate domain
			if not cred.hasDomain( url.netloc ):
				raise APIError("Your domain is not authorized to use this resource", code=401)

			# Set website
			request.website = cred.website

			# Run function
			return func(request, api, *args, **kwargs)

		return wrapper
	return decorator

def require_project_auth():
	"""
	Demand a valid project authentication credentials to be present
	in the header before continuing with the wrapped function.

	This function does not require a protocol wrapper since it 
	operates purely on HTTP level.

	@decorator
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, api="json", *args, **kwargs):

			# Skip if already processed
			if not hasattr(request, 'project'):

				# In GET requests authentication information are
				# passed in the last, auth= parameter
				if request.method == 'GET':

					# Get query string
					query = request.META['QUERY_STRING']

					# Look for 'auth' parameter
					parts = query.split('&auth=', 1)
					if len(parts) == 1:
						raise APIError( "Missing auth= GET parameter", code=400)

					# Check if auth= is the last parameter
					if '=' in parts[1]:
						raise APIError( "auth= must be the last GET parameter", code=400)

					# Validate credentials
					project = _validate_project_auth(parts[0], parts[1])
					if not project:
						raise APIError( "You are not authorized to use this resource", code=401)

					# Store project on request
					request.project = project

				else:

					# For all other HTTP Requests, Authorization iformation are included in 
					# the 'Authorization' header so we cannot process without it
					if not 'HTTP_AUTHORIZATION' in request.META:
						raise APIError( "Missing Authorization header", code=400)

					# Validate credentials
					project = _validate_project_auth(request.body, request.META['HTTP_AUTHORIZATION'])
					if not project:
						raise APIError( "You are not authorized to use this resource", code=401)

					# Store project on request
					request.project = project

			# Run function
			return func(request, api, *args, **kwargs)

		return wrapper
	return decorator
