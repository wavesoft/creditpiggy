from django.shortcuts import render
from django.http import HttpResponse

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import require_project_auth

@render_with_api(context="project.alloc")
@require_project_auth()
def slot_alloc(request, api):
	"""
	Allocate a slot
	"""
	raise APIError("Not implemented", code=501)

@render_with_api(context="project.claim")
@require_project_auth()
def slot_claim(request, api):
	"""
	Claim a slot
	"""
	return { }

@render_with_api(context="project.meta")
@require_project_auth()
def slot_meta(request, api):
	"""
	Define slot metadata
	"""
	return { }

@render_with_api(context="project.counters")
@require_project_auth()
def slot_counters(request, api):
	"""
	Append slot coutners
	"""
	return { }

@render_with_api(context="project.bulk")
@require_project_auth()
def bulk_commands(request, api):
	"""
	Execute a bulk of commands
	"""
	return { }
