
from creditpiggy.api.protocol import APIProtocol
from django.http import HttpResponse

import json

class JSON(APIProtocol):
	"""
	Base class for implementing API protocols
	"""

	#: The identification name of the protocol
	PROTOCOL_NAME = "json"

	def __init__(self, request, context):
		"""
		Initialize the API protocol with the request and context specified
		"""
		APIProtocol.__init__(self, request, context)

		# If we have a POST request, get the JSON payload
		self.data = {}
		if request.method == 'POST':
			self.data = json.loads( request.body )

	def getAll(self):
		"""
		Return all the parameters from the request
		"""

		if request.method == 'POST':
			# On POST requests, return the parsed body
			return self.data
			
		elif self.request.method == 'GET':
			# On GET requests return the query dict
			return self.GET.dict()

	def get(self, parameter, default=None):
		"""
		Get a request parameter, or use the default if missing
		"""

		# On POST request check for the parameter in the body
		if self.request.method == 'POST':

			# Check if we have this parameter in the data
			if parameter in self.data:
				return self.data[ parameter ]
			else:
				return default

		# On GET requests check for the parameter in the URL
		elif self.request.method == 'GET':
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
