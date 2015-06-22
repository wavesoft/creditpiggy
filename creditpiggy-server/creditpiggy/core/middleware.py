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

import pytz
import time

from importlib import import_module
from django.utils import timezone
from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.utils.cache import patch_vary_headers
from django.utils.http import cookie_date
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.signing import BadSignature

class TimezoneMiddleware(object):
	"""
	Set user's preferred timezone upon saving
	"""
	def process_request(self, request):
		tzname = request.session.get('django_timezone')

		# Apply user's timezone
		if request.user.is_authenticated():
			timezone.activate(pytz.timezone(request.user.timezone))

		# Otherwise, detect from session
		elif tzname:
			timezone.activate(pytz.timezone(tzname))
		else:
			timezone.deactivate()

class URLSuffixMiddleware(object):
	"""
	Automatically append ?appid GET parameter in the URL
	when redirecting.
	"""

	def process_response(self, request, response):

		# Include '?webid' if specified on redirect responses
		if hasattr(request, 'webid'):
			if isinstance(response, HttpResponseRedirect):

				# Calculate new URL
				url = response.url
				if '?' in response.url:
					if '&' in response.url:
						url += "&webid=%s" % request.webid
					else:
						url += "webid=%s" % request.webid
				else:
					url += "?webid=%s" % request.webid

				# Create a new object (because 'url' is read-only),
				# but copy all other attributes
				response['Location'] = url

		# Return response
		return response

class SessionWithAPIMiddleware(SessionMiddleware):
	"""
	An extension of the django.contrib.sessions.middleware.SessionMiddleware
	that forks into different session when 'appid' is present in the request.
	"""

	def __init__(self):
		"""
		Initialize SessionWithAPIMiddleware
		"""
		# Initialize local properties
		self.webid = None
		self.webidFromSocial = False
		self.fromSocial = False
		self.cookieName = ""
		# Initialize superclass
		super(SessionWithAPIMiddleware, self).__init__()


	def process_request(self, request):
		"""
		Check for 'appid' presence
		"""

		# Check for social URLs
		self.fromSocial = (request.path.startswith("/complete/")) or (request.path.startswith("/login/"))

		# Check for API ID in : GET, POST, Headers or Cookie
		self.webidFromSocial = False
		self.webid = request.GET.get("webid", None)
		if not self.webid:
			self.webid = request.POST.get("webid", None)
		if not self.webid and 'HTTP_X_WEB_ID' in request.META:
			self.webid = request.META['HTTP_X_WEB_ID']
		if not self.webid and self.fromSocial:
			try:
				self.webid = request.get_signed_cookie(settings.WEBID_COOKIE_NAME, salt=settings.WEBID_COOKIE_SALT)
				self.webidFromSocial = True
			except KeyError:
				self.webid = None
			except BadSignature:
				self.webid = None

		# If there is no API ID, don't override cookie name
		_tmp_name = settings.SESSION_COOKIE_NAME
		if self.webid:
			self.cookieName = settings.SESSION_COOKIE_NAME = "%s_%s" % (settings.SESSION_COOKIE_NAME_API, self.webid)
			# Also store api id in request
			request.webid = self.webid

		# Call super class
		ret = super(SessionWithAPIMiddleware, self).process_request(request)

		# Restore cookie name
		settings.SESSION_COOKIE_NAME = _tmp_name
		return ret

	def process_response(self, request, response):
		"""
		Process response
		"""

		# If there is no API ID, don't override cookie name
		_tmp_name = settings.SESSION_COOKIE_NAME
		if self.webid:
			settings.SESSION_COOKIE_NAME = self.cookieName

		# Call super class
		response = super(SessionWithAPIMiddleware, self).process_response(request, response)

		# Restore cookie name
		settings.SESSION_COOKIE_NAME = _tmp_name

		# Set cryptographic cookie which is used for passing the 'appid' 
		# argument through the log-in mechanism.
		if self.webid and self.fromSocial and not self.webidFromSocial:
			# Set APP ID Cookie
			response.set_signed_cookie(settings.WEBID_COOKIE_NAME,
					self.webid, 
					salt=settings.WEBID_COOKIE_SALT,
					max_age=60, 
					domain=settings.SESSION_COOKIE_DOMAIN,
					path=settings.SESSION_COOKIE_PATH
					)

		elif self.webidFromSocial:
			# Delete APP ID Cookie
			response.delete_cookie(settings.WEBID_COOKIE_NAME,
					domain=settings.SESSION_COOKIE_DOMAIN,
					path=settings.SESSION_COOKIE_PATH
					)

		# Return response
		return response
