
import hashlib

from creditpiggy.api.protocol import APIError
from functools import wraps

def validate_signature(payload, auth):
	"""
	Validate the checksum of the payload using the credentials specified
	"""

	# Split autentication parameter
	auth_parts = auth.lower().split(",")
	if len(auth_parts) != 3:
		raise APIError("Could not parse authentication information")

	# get the digest algoritm used
	(algo, project, digest) = auth_parts

	# Lookup project
	

	print ">>> Payload: '%s'" % payload
	print ">>> Auth: '%s'" % auth

def require_project_auth():
	"""
	Use this decorator
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, api="json", *args, **kwargs):

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
				if not validate_signature(parts[0], parts[1]):
					raise APIError( "You are not authorized to use this resource", code=401)

			else:

				# For all other HTTP Requests, Authorization iformation are included in 
				# the 'Authorization' header so we cannot process without it
				if not 'HTTP_AUTHORIZATION' in request.META:
					raise APIError( "Missing Authorization header", code=400)

				# Validate credentials
				if not validate_signature(request.body, request.META['HTTP_AUTHORIZATION']):
					raise APIError( "You are not authorized to use this resource", code=401)

			# Run function
			return func(request, api, *args, **kwargs)

		return wrapper
	return decorator
