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
from django.shortcuts import render, redirect
from django.contrib.auth import logout as auth_logout

from creditpiggy.core.decorators import render_to

def context(**extra):
	"""
	Common context generator for all templates below
	"""
	return dict({

	}, **extra)

def logout(request):
    """
    Log the user out of any social profile
    """
    auth_logout(request)
    return redirect('/')

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
		return redirect(reverse("frontend.profile"))
	else:
		return redirect(reverse("frontend.login"))

@render_to("login.html")
def login(request):
	"""
	Login page
	"""
	if request.user.is_authenticated():
		return redirect(reverse("frontend.profile"))

	return { }

@render_to("profile.html")
def profile(request):
	"""
	User profile page
	"""
	if not request.user.is_authenticated():
		return redirect(reverse("frontend.login"))

	return { }