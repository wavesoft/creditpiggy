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

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect

from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

from creditpiggy.frontend.views import context

from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *

@login_required()
@render_to("projects.html")
def list(request):
	"""
	List projects page
	"""

	# Return context
	return context(request)

@login_required()
@render_to("project.html")
def details(request, slug=""):
	"""
	Display project details
	"""	

	# Lookup project based on slug
	try:
		if (slug.isdigit()):
			project = PiggyProject.objects.get(id=int(slug))
		else:
			project = PiggyProject.objects.get(slug=slug)
	except PiggyProject.DoesNotExist:

		# Render error page
		return render_to_response("error.html", context(
				message="Could not find the project specified!"
			))

	# Get project achievements
	achievements = project.achievementStatus(request.user)

	# Return context
	return context(request,
		project=project,
		achievements=achievements,
		counters=project.metrics().counters()
		)

@login_required()
@render_to("dashboard.html")
def dashboard(request, page):
	"""
	Display project dashboard
	"""

	# Return context
	return context(request,
		page=page
		)
