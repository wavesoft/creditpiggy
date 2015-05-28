from django.shortcuts import render
from django.http import HttpResponse

from creditpiggy.api.utils.jsonapi import APIResponse, APIError
from creditpiggy.api.utils.token import requireUserAuthToken

@requireUserAuthToken("project_id")
def project_serve(request, project_id, token_id):
	"""
	Reserve a project slot
	"""

	# Return API response
	return APIResponse({
			'project': project_id
		})


@requireUserAuthToken("project_id")
def project_report(request, project_id, token_id):
	"""
	Report back to a project slot
	"""

	# Return API response
	return APIResponse({
			'project': project_id
		})

