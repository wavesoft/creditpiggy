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

def dump_var(var, prefix=""):
	"""
	Recursively dump the specified variable
	"""
	ans = []

	if isinstance(var, list) or isinstance(var, tuple):
		if prefix:
			prefix = prefix + "."
		i = 0
		for v in var:
			ans += dump_var( v, "%s%i" % ( prefix, i ) )
			i += 1

	elif isinstance(var, dict):
		if prefix:
			prefix = prefix + "."
		for k,v in var.iteritems():
			ans += dump_var( v, "%s%s" % (prefix, k) )

	else:
		ans.append("%s: %s" % (prefix, str(var)))

	return ans

class TEXTProtocol(APIProtocol):
	"""
	TEXT Implementation of the CreditPiggy API Protocol

	Supports POST requests with TEXT payload or GET requests 
	with classic GET messages.
	"""

	#: The identification name of the protocol
	PROTOCOL_NAME = "text"

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

					# Tokenize body
					self.data = {}
					parts = self.request.body.split(",")
					for p in parts:
						if not '=' in p:
							raise APIError("Malformed protocol data in POST")
						kv = p.split("=")
						self.data[kv[0]] = kv[1]

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

		# Get parameters
		args = self.getAll()

		# Require parameter if requested
		if not parameter in args:
			if required:
				return APIError("Missing required parameter '%s'" % parameter)
			else:
				return default

		# Otherwise get with default
		return args[parameter]

	def render_success(self, data):
		"""
		Render the specified dictionary with a success response
		"""

		# Prepare response
		response = ""

		# If data is list or data contains only
		# one, list field, just dump the contents
		if isinstance(data, list):
			# Create payload
			response = "\n".join(data) + "\n"
		elif (isinstance(data, dict) and (len(data) == 1) and isinstance(data.values()[0], list)):
			# Create payload
			response = "\n".join(data.values()[0]) + "\n"

		# Process dictionaries
		elif isinstance(data, dict):
			# Convert dict to TEXT
			response = "\n".join(dump_var(data))

		# Otherwise stringify
		else:
			response = str(data)

		# Build an HTTP Response
		res = HttpResponse(
				response, 
				content_type="text/plain", 
				status=200
			)
		
		# Insert headers
		for k,v in self.headers.iteritems():
			res[k] = v

		# Return response
		return res

	def render_error(self, data, code=None):
		"""
		Render the specified dictionary with a error response
		"""

		# Prepare message
		response = ""

		# If data is list or data contains only
		# one, list field, just dump the contents
		if isinstance(data, list):
			# Create payload
			response = "\n".join(data) + "\n"
		elif (isinstance(data, dict) and (len(data) == 1) and isinstance(data.values()[0], list)):
			# Create payload
			response = "\n".join(data.values()[0]) + "\n"

		# Process dictionaries
		elif isinstance(data, dict):
			# Convert dict to TEXT
			response = "\n".join(dump_var(data))

		# Otherwise stringify
		else:
			response = str(data)


		# Check if we have an error code
		if code is None:
			code = 500

		# Build an HTTP Response
		res = HttpResponse(
				"ERROR\n%s\n" % response,
				content_type="text/plain", 
				status=code
			)

		# Insert headers
		for k,v in self.headers.iteritems():
			res[k] = v

		# Return response
		return res
