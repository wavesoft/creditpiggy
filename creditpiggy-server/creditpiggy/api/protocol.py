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

from functools import wraps
from django.http import HttpResponse
from django.conf import settings
import importlib
import json

#: Supported protocols cache
_supported_protocols = None

class APIProtocol:
	"""
	Base class for implementing API protocols
	"""

	#: The identification name of the protocol
	PROTOCOL_NAME = "none"

	def __init__(self, request, context):
		"""
		Initialize the API protocol with the request and context specified
		"""
		self.request = request
		self.context = context
		self.headers = {}

	def get(self, parameter, default=None, required=False):
		"""
		Get a request parameter, or use the default if missing
		"""
		raise NotImplementedError()

	def render_success(self, data):
		"""
		Render the specified dictionary with a success response
		"""
		raise NotImplementedError()

	def render_error(self, data, code=None):
		"""
		Render the specified dictionary with a error response
		"""
		raise NotImplementedError()

	def add_header(self, header, value):
		"""
		Add a header to be part of the HTTP response
		"""
		self.headers[header] = value

class APIError(Exception):
	"""
	An exception that when fired will be handled by the api wrapper
	in order to provide the error details.
	"""
	def __init__(self, message, data={}, code=500):
		Exception.__init__(self)

		# Update data with message
		data['message'] = message
		self.message = message

		# Keep data and code as details
		self.data = data
		self.code = code

	def __str__(self):
		"""
		Stringify exception to the message
		"""
		return message

def _get_supported_protocols():
	"""
	Internal function to populate the supported protocols dictionary.

	This is used for optimizing the performance of incoming requests, since
	loading the entire list of modules on every request might be quite the
	performance impact.
	"""

	# Populate dictionary
	global _supported_protocols
	if not _supported_protocols:

		# Initialize protocols dict
		_supported_protocols = {}

		# Iterate over registered api protocols
		for proto_mod in settings.CREDITPIGGY_API_PROTOCOLS:

			# Split module/class
			parts = proto_mod.split(".")
			p_module = ".".join(parts[0:-1])
			p_class = parts[-1]

			# Import module
			mod = importlib.import_module(p_module)

			# Get class reference
			cls = getattr(mod, p_class, None)
			if not cls:
				raise ImportError("Could not find class %s in module %s" % (p_class, p_module))

			# Get the protocol name and store on supported protocols dictionary
			_supported_protocols[ cls.PROTOCOL_NAME ] = cls

	# Return the dictionary
	return _supported_protocols

def render_with_api(context=None, protocol=None):
	"""
	Decorator for automatically creating the appropriate protocol object
	upon receiving the request and 
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):

			# Skip if already processed
			if hasattr(request, 'proto'):
				return func(request, api, *args, **kwargs)

			# Override 'api' if we have protocol defined
			if not protocol is None:
				api = protocol
			else:
				if 'api' in kwargs:
					api = kwargs['api']
				else:
					api = 'json'

			# Get protocol
			prot = _get_supported_protocols()
			if api is None:
				api = prot.keys()[0]

			# Ensure the protocol exists and is valid
			if not api in prot:
				return HttpResponse(
						"Unknown API protocol '%s' requested" % api,
						content_type="text/plain",
						status=500
					)

			# Instantiate and store protocol in request
			request.proto = prot[api]( request, context )

			# Exception guard
			try:

				# Handle request
				out = func(request, *args, **kwargs)

				# Render with protocol renderer if result is a dict or None
				if out is None:
					return request.proto.render_success({ })
				elif isinstance(out, dict):
					return request.proto.render_success(out)
				
				# Otherwise return the response as-is
				return out

			except APIError as e:
				# Catch APIErrors and convert them to error responses
				return request.proto.render_error(e.data, e.code)

			return out
		return wrapper
	return decorator
