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