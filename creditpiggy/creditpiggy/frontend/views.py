from django.http import HttpResponse, HttpResponseBadRequest
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

@render_to("home.html")
def home(request):
	"""
	Landing page
	"""
	return { }

@render_to("profile.html")
def profile(request):
	"""
	User profile page
	"""
	return { }