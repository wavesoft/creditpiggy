from django.http import HttpResponse
import json

def APIResponse(data={}):
	"""
	Create a JSON API response
	"""

	# Prepare core response
	response = {
		'result': 'ok',
	}

	# Include data
	if type(data) is dict:
		response.update(data)

	# Return an HTTP Response
	return HttpResponse(
			json.dumps(response), 
			content_type="application/json", 
			status=200
		)

def APIError(message=None, code=None):
	"""
	Create a JSON API error
	"""
	
	# Prepare core response
	response = {
		'result': 'error'
	}

	# Put error message
	if not message is None:
		response['message'] = message

	# Check if we have an error code
	if code is None:
		code = 500

	# Return an HTTP Response
	return HttpResponse(
			json.dumps(response), 
			content_type="application/json", 
			status=code
		)
