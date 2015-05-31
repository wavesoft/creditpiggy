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

from __future__ import absolute_import

from creditpiggy.api.protocol import APIProtocol, APIError
from django.http import HttpResponse

import json

class JSONProtocol(APIProtocol):
	"""
	JSON Implementation of the CreditPiggy API Protocol

	Supports POST requests with JSON payload or GET requests 
	with classic GET messages.
	"""

	#: The identification name of the protocol
	PROTOCOL_NAME = "json"

	def __init__(self, request, context):
		"""
		Initialize the API protocol with the request and context specified
		"""
		APIProtocol.__init__(self, request, context)

		# If we have a POST request, get the JSON payload
		self.data = None

	def getAll(self):
		"""
		Return all the parameters from the request
		"""

		if self.request.method == 'POST':

			# Populate missing self.data
			if not self.data:
				try:
					self.data = json.loads( self.request.body )
				except ValueError:
					raise APIError("Could not parse JSON request", code=400)

			# On POST requests, return the parsed body
			return self.data
			
		elif self.request.method == 'GET':
			# On GET requests return the query dict
			return self.request.GET.dict()

	def get(self, parameter, default=None, required=False):
		"""
		Get a request parameter, or use the default if missing
		"""

		# On POST request check for the parameter in the body
		if self.request.method == 'POST':

			# Populate missing self.data
			if not self.data:
				try:
					self.data = json.loads( self.request.body )
				except ValueError:
					raise APIError("Could not parse JSON request", code=400)

			# Check if we have this parameter in the data
			if parameter in self.data:
				return self.data[ parameter ]
			else:
				if required:
					return APIError("Missing required parameter '%s'" % parameter)
				return default

		# On GET requests check for the parameter in the URL
		elif self.request.method == 'GET':

			# Require parameter if requested
			if required and not parameter in self.request.GET:
				return APIError("Missing required parameter '%s'" % parameter)

			# Otherwise get with default
			return self.request.GET.get( parameter, default )

	def render_success(self, data):
		"""
		Render the specified dictionary with a success response
		"""

		# Prepare core response
		response = {
			'result': 'ok',
		}

		# Include data
		if isinstance(data, dict):
			response.update(data)

		# Return an HTTP Response
		return HttpResponse(
				json.dumps(response), 
				content_type="application/json", 
				status=200
			)

	def render_error(self, data, code=None):
		"""
		Render the specified dictionary with a error response
		"""

		# Prepare core response
		response = {
			'result': 'error'
		}

		# Put error message
		if isinstance(data, dict):
			response.update(data)

		# Check if we have an error code
		if code is None:
			code = 500

		# Return an HTTP Response
		return HttpResponse(
				json.dumps(response), 
				content_type="application/json", 
				status=code
			)
