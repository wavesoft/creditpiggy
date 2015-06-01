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

from functools import wraps

from django.template import RequestContext
from django.shortcuts import render_to_response

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
