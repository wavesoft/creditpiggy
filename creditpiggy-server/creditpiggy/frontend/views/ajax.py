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

import time
from django.db.models import Q

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.core.models import to_dict, PiggyProject

#######################################################
# Utility functions
#######################################################

def build_filter( request, accept=None ):
	"""
	Build DJango filter according to the request
	"""

	# Prepare Q kwargs
	kwargs = {}

	# Process request
	for k,v in request.iteritems():

		# Handle only accepted keywords
		if not (accept is None) and not (k in accept):
			continue

		# Check matching values
		v = str(v)

		# [==] Excact
		if v[:2] == "==":
			kwargs[k] = v[2:]

		# [<=] Less than or equal
		elif v[:2] == "<=":
			kwargs["%s__lte" % k] = v[2:]

		# [>=] Greater than or equal
		elif v[:2] == ">=":
			kwargs["%s__gte" % k] = v[2:]

		# [~=] Startswith
		elif v[:2] == "~=":
			kwargs["%s__startswith" % k] = v[2:]

		# [=~] Endswith
		elif v[:2] == "~=":
			kwargs["%s__endswith" % k] = v[2:]

		# [~] Contains
		elif v[:1] == "~":
			kwargs["%s__contains" % k] = v[1:]

		# [<] Less than
		elif v[:1] == "<":
			kwargs["%s__lt" % k] = v[1:]

		# [>] Greater than or equal
		elif v[:1] == ">":
			kwargs["%s__gt" % k] = v[1:]

	# Return a Q object that contains the specified KWargs
	return Q(**kwargs)

def build_ts_labels(timestamps, interval=1, format="%d/%m/%Y %H:%M:%S"):
	"""
	Create string labels for the specified timestamps, keepong
	only the ones every [interval].
	"""

	i = 0
	labels = []
	for ts in timestamps:

		# Add blanks if missing interval
		if (i % interval) != 0:
			labels.append("")
			continue

		# Parse timestamp
		t = time.localtime(float(ts))
		labels.append(time.strftime(format, t))

	# Return labels
	return labels

#######################################################
# View functions
#######################################################

@login_required()
@render_with_api(context="frontend.ajax.profile", protocol="json")
def profile(request, cmd):
	"""
	Handle AJAX profile requests
	"""

	# Update a profile field
	# -------------------------------
	if cmd == "set":

		# Require post method
		if request.method != 'POST':
			raise APIError("Profile information are only updated via POST")

		# Get parameters
		u_args = request.proto.getAll()

		# Update fields
		if 'name' in u_args:
			request.user.display_name = u_args['name']

		# Save record
		request.user.save()

	else:
		raise APIError("Unknown command")

@login_required()
@render_with_api(context="frontend.ajax.fetch", protocol="json")
def fetch(request, cmd):
	"""
	Pagination/graduate loading for various objects
	"""

	# Query projects
	# -------------------------------
	if cmd == "projects":

		# Prepare Query
		query = build_filter( request.proto.getAll(), [ 'display_name', 'desc' ] )

		# Get all relevant projects
		projects = PiggyProject.objects.filter( query )
		paginator = Paginator( projects, 10 ) # Fetch 10 projects per page

		# Get projects on pages
		page = request.GET.get('page')
		if not page:
			page = 1

		# Try to render
		try:
			pprojects = paginator.page(page)
		except PageNotAnInteger:
			raise APIError("Page is not a number", code=400)
		except EmptyPage:
			raise APIError("No more pages", code=404)

		# Render pages
		elmList = []
		for p in pprojects:

			# Get all project achievements
			elmList.append( to_dict(p) )

		# Return projects
		return {
			'list': elmList,
			'page': page,
			'pages': paginator.num_pages
		}

	elif cmd == "dashboard":

		# Query projects that I participated
		PiggyProject.objects.all().select_related("school")

	else:
		raise APIError("Unknown command")

@login_required()
@render_with_api(context="frontend.ajax.graph", protocol="json")
def graph(request, cmd):
	"""
	Graph data for various metrics
	"""

	# User graphs
	# -------------------------------
	if cmd == "user":

		# Get user metrics
		u_metrics = request.user.metrics()

		# What to observe
		obs_metrics = [ 'credits' ]
		obs_legends = [ 'Credits' ]
		obs_tss = [ 'hourly', 'daily', 'weekly', 'monthly' ]

		# Compile response
		ans = {}
		for ts_name in obs_tss:

			# Get timeseries
			(ts, val) = u_metrics.timeseries(ts_name, metric=obs_metrics)

			# Convert timeseries to milliseconds
			ts = map(lambda x: int(float(x)*1000), ts)

			# Store in response
			ans[ts_name] = {
				"labels" : ts,
				"series" : val,
				"legends": obs_legends
			}

		# Return values
		return {
			'plots': ans
		}

	else:
		raise APIError("Unknown command")
