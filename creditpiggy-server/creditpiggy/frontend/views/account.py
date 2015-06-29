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

from social.apps.django_app.default.models import UserSocialAuth

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from creditpiggy.frontend.views import context, url_suffix

from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *
from creditpiggy.api.auth import sso_logout, website_from_request
from creditpiggy.api import information

#######################################################
# Utility functions
#######################################################

def releasable_workers( request, user, website ):
	"""
	Return a list of workers that will/should be released
	upon logging out.
	"""

	# If we don't have website, say nothing
	if website is None:
		return None

	# Fetch the linked list of workers from session
	workers = []
	if 'workers' in request.session:
		workers = request.session['workers']
	if not workers:
		return None

	# Fetch all machines that would be disposed
	# upon logging out.
	units = ComputingUnit.objects.filter(
			owner=user, id__in=workers
		)

	# Check if counter is bigger than 0
	if units.count() == 0:
		return None

	# Return units otherwise
	return units

#######################################################
# View functions
#######################################################

@render_to("done_logout.html")
def logout(request):
	"""
	Log the user out of any social profile
	"""

	# Get website
	website = website_from_request( request, whitelistPath=True )

	# Check if we have confirm flag
	confirm = False
	if 'confirm' in request.GET:
		confirm = bool(request.GET['confirm'])

	# Confirm if there are workers to be released
	if not (website is None):
		workers = releasable_workers( request, request.user, website )
		if not workers is None:
			if not confirm:

				# Pluralize
				plural = ""
				if workers.count() > 1:
					plural = "s"

				# Render message
				return render_to_response("confirm.html", context(request,
						body="<p>It looks that your account is linked with <strong>%i</strong> computing unit%s. By logging out you are going to release them and make them available for anyone to claim.</p>" % ( workers.count(), plural ) + \
							 "<p>You will not loose your current credits, but you will no longer receive new credits from them.</p>" + \
							 "<p>Just log-in at any time if you want to link them to your account again.</p>",
						icon="/static/frontend/img/pc-warning.png",
						link_ok=reverse("frontend.logout") + "?confirm=1",
						link_cancel=reverse("frontend.profile"),
					))
			else:
				# Release all workers
				workers.update( owner=None, website=None )

	# Delete sso tokens
	if website:
		sso_logout( request.user, website )

	# Logout the user
	auth_logout(request)

	# Render the logout page
	return context(request)

@render_to("done_login.html")
def login_ack(request):
	"""
	Login confirm, mainly used for callback to parent API
	"""

	# Check if this is a website login page
	website = website_from_request( request, whitelistPath=True )

	# If we are from a website, redirecto to website status, otherwuse to the user profile
	next_url = reverse("frontend.login")
	if website:
		next_url = reverse("frontend.website.status", kwargs={ "slug": website.slug })

	# Return context
	return context(request,
			session=json.dumps(information.compile_session(request)),
			next=next_url
		)

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

	# Check if this is a website login page
	website = website_from_request( request, whitelistPath=True )

	# If already authenticated, redirect
	if request.user.is_authenticated():
		if 'next' in request.GET:
			return redirect(request.GET['next'])
		else:
			return redirect(reverse("frontend.profile") )

	# Return context
	return context(request,
			website=website
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

	# Lookup all the available profiles to mark
	social_links = {
		"twitter": True,
		"facebook": True,
		"google_oauth2": True,
		"live": True
	}

	# Hide all the used providers
	for p in UserSocialAuth.objects.filter( user=request.user ):
		social_links[p.provider.replace("-","_")] = False

	# Get website
	website = website_from_request( request, whitelistPath=True )

	# Return context
	return context(request,
			session=json.dumps(information.compile_session(request)),
			social_links=social_links,
			show_social=any(social_links.values()),
			website=website,
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

@render_to("email/welcome.html")
@login_required()
def test(request):
	"""
	Testing endpoint
	"""

	a = Achievement.objects.all()[0]
	p = PiggyProject.objects.all()[0]

	ctx = context(request,
		achievement=a, 
		project=p,
		base_url=settings.BASE_URL,
		)

	return ctx

	return redirect(reverse("frontend.profile"))
