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

import re
from functools import wraps

from django.template import RequestContext
from django.shortcuts import render_to_response
from django.utils.decorators import available_attrs
from django.views.decorators.cache import cache_page

RE_VALID_BG = re.compile(r'^[0-f][0-f][0-f]([0-f][0-f][0-f])?$')

def render_to(tpl):
	"""
	Use this decorator in a view function and return a dictionary object.
	It will take care of rendering it to the specified template.
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			out = func(request, *args, **kwargs)
			if isinstance(out, dict):
				out = render_to_response(tpl, out, RequestContext(request))
			return out
		return wrapper
	return decorator

def cache_page_per_user(timeout):
	"""
	Use this decorator in a view to cache it's response per user and not globaly
	"""
	def decorator(func):
		@wraps(func)
		def wrapper(request, *args, **kwargs):
			# Calculate prefix per user
			user_id = "page_all"
			if request.user.is_authenticated():
				user_id = "page_u%i" % request.user.id

			# Wrap per user
			cached = cache_page(timeout, key_prefix=user_id)(func)
			return cached(request, *args, **kwargs)
		return wrapper
	return decorator

def accept_bg_option(func):
	"""
	Accept background altering options (used by embed)
	WARNING: This MUST be used before render_width
	"""
	@wraps(func)
	def wrapper(request, *args, **kwargs):
		out = func(request, *args, **kwargs)
		if isinstance(out, dict):
			if 'bg' in request.GET:
				bg = request.GET['bg']
				if RE_VALID_BG.match(bg):

					# Convert 3-notation to 6-notation
					if len(bg) == 3:
						bg = bg[0] + bg[0] + bg[1] + bg[1] + bg[2] + bg[2]

					# Parse to rgb
					r = int(bg[0:2], 16)
					g = int(bg[2:4], 16)
					b = int(bg[4:6], 16)

					# Inject additional details
					out['bg_color'] = bg
					out['bg_color_r'] = r
					out['bg_color_g'] = g
					out['bg_color_b'] = b
		return out
	return wrapper

