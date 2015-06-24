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

	# Get all the observable metrics
	vmetric = { }
	for m in website.visual_metrics.all():
		# Keep metric
		vmetric[m.name] = to_dict( m )
		# Reset value

		vmetric[m.name]['value'] = None
		vmetric[m.name]['samples'] = 0

	# Aggregate information from all projects
	projects = []
	achievements = []
	for p in website.projects.all():

		# Get project metrics
		pm = p.metrics()

		# Get project record
		projects.append( to_dict(p) )

		# Get project achievements
		achievements += p.achievementStatus(request.user)

		# Accumulate the counters of interesting metrics
		for k, m in vmetric.iteritems():

			# Get counter value
			counter = pm.counter(k, "")
			if not counter:
				counter = 0
			elif '.' in str(counter):
				counter = float(counter)
			else:
				counter = int(counter)

			# Increment samples
			m['samples'] += 1

			# Apply summarization method
			if m['value'] is None:
				m['value'] = counter
			else:
				if (m['sum_method'] == VisualMetric.ADD) or (m['sum_method'] == VisualMetric.AVERAGE):
					m['value'] += counter
				elif m['sum_method'] == VisualMetric.MINIMUM:
					if counter < m['value']:
						m['value'] = counter
				elif m['sum_method'] == VisualMetric.MAXIMUM:
					if counter > m['value']:
						m['value'] = counter

	# Apply average on metrics
	for k, m in vmetric.iteritems():
		if (m['sum_method'] == VisualMetric.AVERAGE):
			m['value'] /= m['samples']

	# Return context
	return context(request,
			website=website,
			about_body=website.desc,
			header_background=website.header_background,
			header_foreground=website.header_foreground,
			header_image=website.header_image,
			metrics=vmetric.values(),
			projects=projects,
			achievements=achievements,
		)

