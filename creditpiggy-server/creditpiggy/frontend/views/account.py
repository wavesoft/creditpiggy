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
import hashlib
import re

from social.apps.django_app.default.models import UserSocialAuth

from django.http import HttpResponse, HttpResponseBadRequest
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, redirect
from django.contrib.auth import logout as auth_logout
from django.contrib.auth import login as auth_login

from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from creditpiggy.frontend.views import context, url_suffix

from creditpiggy.core.ranking import rank_user, rank_user_campaign, rank_user_project
from creditpiggy.core.decorators import render_to
from creditpiggy.core.models import *
from creditpiggy.core.utils import VisualMetricsSum
from creditpiggy.api.auth import sso_logout, website_from_request
from creditpiggy.api import information

from creditpiggy.core.achievements import personal_next_achievement, campaign_next_achievement

NOT_NUMBERS = re.compile('[^0-9]')

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

def login_pin(request):
	"""
	Check if we can log-in with pin
	"""

	# Get fields from POST
	token = request.POST['token']
	pin = request.POST['pin']
	email = request.POST['email']

	# Get candidate user
	user = PiggyUser.fromAnonymousEmail( email, False )
	if not user:
		return render_to_response("error.html", context(request,
				message="Could not find the user specified!"
			))

	# Get login token
	try:
		loginToken = PiggyUserPINLogin.objects.get( user=user )
	except PiggyUserPINLogin.DoesNotExist:
		return render_to_response("error.html", context(request,
				message="A PIN was never sent to this e-mail address!"
			))

	# Validate token
	if token:
		if loginToken.token != token:
			return render_to_response("error.html", context(request,
					message="Mismatch offline PIN validation!"
				))

	# Validate pin
	elif pin:
		pin = NOT_NUMBERS.sub("", pin)
		if loginToken.pin != pin:
			return render_to_response("error.html", context(request,
					message="Wrong PIN specified!"
				))


	# Login & redirect to login ack
	user.backend = "django.contrib.auth.backends.ModelBackend"
	auth_login( request, user )
	return redirect( reverse("frontend.login.done") )

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

	# Include pin token if we have a pin token
	pin_token=request.session.get('pin_token', None),
	pin_hash=""
	if not pin_token is None:
		try:
			pin_hash=hashlib.sha256(request.user.email.lower()).hexdigest(),
		except AttributeError:
			pin_token=None

	# Return context
	return context(request,
			session=json.dumps(information.compile_session(request)),
			next=next_url,
			pin_token=pin_token,
			pin_hash=pin_hash,
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

@ensure_csrf_cookie
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

@render_to("share/achievement.html")
@login_required()
def test(request):
	"""
	Testing endpoint
	"""
	return context(request,
		achievement=AchievementInstance.objects.all()[0], 
		user=request.user
		)


@login_required()
@render_to("dashboard_overview.html")
def dashboard_overview_overall(request):
	"""
	Display user's overall contribution to all projects
	"""

	# Get all projects that I participated
	u_projects = ProjectUserRole.objects.filter( user=request.user )
	# Get all campaigns that I participated
	u_campaigns = CampaignUserCredit.objects.filter( user=request.user )

	# Get user metrics
	user_counters = request.user.metrics().counters()

	# Collect user metrics
	umetric = VisualMetricsSum( VisualMetric.objects.all() )
	umetric.merge( user_counters )
	umetric.finalize()

	# Collect all achievements
	achievements = request.user.achievementStatus()

	# Return context
	return context(request,
		page="overview",
		u_projects=u_projects,
		u_campaigns=u_campaigns,
		achievements=sorted(achievements, key=lambda a: a['achievement'].id),
		metrics=umetric.values(),
		candidate_achievement=personal_next_achievement( request.user ),

		overview_type="Personal",
		title="My overall participation",
		profile=request.user,
		credits=int(user_counters.get('credits',0)),
		rank=rank_user( request.user ),

		)


@login_required()
@render_to("dashboard_overview.html")
def dashboard_overview_project(request, project):
	"""
	Display user dashboard, focused on specified project
	"""
	
	# Get all projects that I participated
	u_projects = ProjectUserRole.objects.filter( user=request.user )
	# Get all campaigns that I participated
	u_campaigns = CampaignUserCredit.objects.filter( user=request.user )

	# Get relevant project-user role
	pur = u_projects.filter( id=int(project) ).get()

	# Create visual metrics
	umetric = VisualMetricsSum( pur.project.visual_metrics.all().order_by('-priority') )
	umetric.merge( pur.metrics() )
	umetric.finalize()

	# Collect achievements
	achievements = pur.project.achievementStatus(request.user, onlyAchieved=True)

	# Return context
	return context(request,
		page="overview",
		u_projects=u_projects,
		u_campaigns=u_campaigns,
		profile=request.user,
		project_id=int(project),
		achievements=sorted(achievements, key=lambda a: a['achievement'].id),
		metrics=umetric.values(),
		candidate_achievement=personal_next_achievement( request.user, project=pur.project ),

		overview_type="Project",
		title="My participation in %s" % pur.project.display_name,
		credits=pur.credits,
		rank=rank_user_project( pur ),

		)

@login_required()
@render_to("dashboard_overview.html")
def dashboard_overview_campagin(request, campaign):
	"""
	Display user dashboard, focused on specified campaign
	"""
	
	# Get all projects that I participated
	u_projects = ProjectUserRole.objects.filter( user=request.user )
	# Get all campaigns that I participated
	u_campaigns = CampaignUserCredit.objects.filter( user=request.user )

	# Get relevant campaign info
	cur = u_campaigns.filter( id=int(campaign) ).get()

	# Get candidate achievement
	candidate_achievement = campaign_next_achievement( cur.campaign )

	# Get campaign achievements
	project_achievements = []
	campaign_achievements = cur.campaign.achievementStatus()

	# Get metrics of all projects
	campaign_project_metrics = []
	for project in cur.campaign.website.projects.all():

		# Collect one of each visual metric
		metrics = project.visual_metrics.all().order_by('-priority')
		for m in metrics:
			if not m in campaign_project_metrics:
				campaign_project_metrics.append(m)

		# Collect project achievements
		project_achievements += project.achievementStatus(request.user, onlyAchieved=True)
		
		# # Get candidate achievement in this project
		# if not candidate_achievement:
		# 	candidate_achievement = personal_next_achievement( request.user, project=project )

	# Create visual metrics
	umetric = VisualMetricsSum( campaign_project_metrics )
	umetric.merge( cur.metrics() )
	umetric.finalize()

	# Return context
	return context(request,
		page="overview",
		u_projects=u_projects,
		u_campaigns=u_campaigns,
		profile=request.user,
		campaign_id=int(campaign),
		achievements=sorted(project_achievements, key=lambda a: a['achievement'].id),
		metrics=umetric.values(),
		candidate_achievement=candidate_achievement,

		overview_type="Project",
		campaign_achievements=sorted(campaign_achievements, key=lambda a: a['achievement'].id),
		title="My participation in %s" % cur.campaign.name,
		credits=cur.credits,
		rank=rank_user_campaign( cur ),

		)

@login_required()
@render_to("dashboard_settings.html")
def dashboard_settings(request):
	"""
	Display user's settings
	"""

	# Return context
	return context(request,
		page="settings",
		profile=request.user
		)

@login_required()
@render_to("dashboard_history.html")
def dashboard_history(request):
	"""
	Display user's settings
	"""

	# Return context
	return context(request,
		page="history"
		)
