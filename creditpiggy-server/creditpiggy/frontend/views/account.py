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

import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import EmailMessage

from creditpiggy.frontend.views import context, url_suffix

from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *
from creditpiggy.api.auth import sso_logout, website_from_request
from creditpiggy.api import information

@render_to("logout.html")
def logout(request):
	"""
	Log the user out of any social profile
	"""

	# Delete sso tokens
	website = website_from_request( request, whitelistPath=True )
	if website:
		sso_logout( request.user, website )

	# Logout the user
	auth_logout(request)

	# Render the logout page
	return context(request)

def link(request, provider):
	"""
	Link currently registered profile with another provider
	"""
	return redirect( "/login/%s/?mode=link" % provider )

def home(request):
	"""
	Landing page
	"""
	if request.user.is_authenticated():
		return redirect(reverse("frontend.profile") )
	else:
		return redirect(reverse("frontend.login") )

@render_to("login.html")
def login(request):
	"""
	Login page
	"""

	# Check if this is a project login page
	project = None
	if 'project' in request.GET:
		try:
			project = PiggyProject.objects.get( uuid=request.GET['project'] )
		except PiggyProject.DoesNotExist:
			project = None

	# If already authenticated, redirect
	if request.user.is_authenticated():
		if 'next' in request.GET:
			return redirect(request.GET['next'])
		else:
			return redirect(reverse("frontend.profile") )

	# Return context
	return context(request,
			project=project
		)

@ensure_csrf_cookie
@render_to("profile.html")
def profile(request):
	"""
	User profile page
	"""
	# Redirect if not logged in
	if not request.user.is_authenticated():
		return redirect(reverse("frontend.login"))

	# Return context
	return context(request,
			session=json.dumps(information.compile_session(request))
		)

@render_to("status.html")
def status(request):
	"""
	User status page
	"""
	if not request.user.is_authenticated():
		return redirect(reverse("frontend.login"))

	# Get projects
	projects = ProjectUserCredit.objects.filter( user=request.user )

	# Return context
	return context(request,
			projects=projects
		)

@render_to("credits.html")
def credits(request):
	"""
	User status page
	"""
	if not request.user.is_authenticated():
		return redirect(reverse("frontend.login"))

	# Get credit slots
	slots = CreditSlot.objects \
		.filter( project=request.GET.get('project', None) ) \
		.order_by( '-status' )

	# Return context
	return context(request,
		slots=slots
		)

@login_required()
def test(request):
	"""
	Testing endpoint
	"""

	mail = EmailMessage( body="Testing", subject="Tosting", to=("johnys2@gmail.com",) )
	mail.send()

	return redirect(reverse("frontend.profile"))
