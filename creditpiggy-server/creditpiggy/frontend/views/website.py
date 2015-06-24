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
from creditpiggy.api.auth import website_from_request

def auto(request):
	"""
	Automatically redirect to website or website listing
	"""

	# Check for website, detected by ?webid=xxx
	website = website_from_request(request, whitelistPath=True)

	# Redirect accordingly
	if not website:
		return redirect(reverse("frontend.profile") )
	else:
		return redirect(reverse("frontend.website.status", kwargs={'urlid': website.urlid} ))

@render_to("website.html")
def status(request, urlid=""):
	"""
	Website status page
	"""

	# Lookup website based on urlid
	try:
		if (urlid.isdigit()):
			website = Website.objects.get(id=int(urlid))
		else:
			website = Website.objects.get(urlid=urlid)
	except Website.DoesNotExist:

		# Render error page
		return render_to_response("error.html", context(
				message="Could not find the website specified!"
			))

	# Return context
	return context(request,
			website=website,
			header_background=website.header_background,
			header_foreground=website.header_foreground,
			header_image=website.header_image,
			metrics=[
				{
					'display_name': 'First test',
					'icon': 'fa fa-clock-o',
					'value': 123142,
					'units': 'min',
				},
				{
					'display_name': 'First test',
					'icon': 'fa fa-clock-o',
					'value': 123142,
					'units': 'min',
				},
				{
					'display_name': 'First test',
					'icon': 'fa fa-clock-o',
					'value': 123142,
					'units': 'min',
				}
			]
		)

