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
import datetime
from django.db.models import Q

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core import serializers

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import require_valid_user
from creditpiggy.core.models import to_dict, PiggyProject, Achievement

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

@render_with_api(context="frontend.ajax.profile", protocol="json")
@require_valid_user()
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
		elif 'email_achievement' in u_args:
			request.user.email_achievement = (int(u_args['email_achievement']) == 1)
		elif 'email_projects' in u_args:
			request.user.email_projects = (int(u_args['email_projects']) == 1)
		elif 'email_surveys' in u_args:
			request.user.email_surveys = (int(u_args['email_surveys']) == 1)
		elif 'priv_leaderboards' in u_args:
			request.user.priv_leaderboards = (int(u_args['priv_leaderboards']) == 1)

		# Save record
		request.user.save()

	else:
		raise APIError("Unknown command")

@render_with_api(context="frontend.ajax.fetch", protocol="json")
@require_valid_user()
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

			# Convert project record to dictionary
			project = to_dict(p)

			# Get all project achievements
			project['achievements'] = []
			for a in p.achievements.all():
				project['achievements'].append(
					to_dict(a)
					)

			# Store project details
			elmList.append( project )

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

@render_with_api(context="frontend.ajax.graph", protocol="json")
@require_valid_user()
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
		obs_tss 	= [ 'hourly', 'daily', 'weekly', 'monthly' ]
		ots_ts_fn	= [
			lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%H:%M'),
			lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%a'),
			lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%m/%d'),
			lambda x: datetime.datetime.fromtimestamp(int(x)).strftime('%b'),
		]

		ts_size = []
		ts_values = []
		ts_legends = []

		# Compile response
		for i in range(0, len(obs_tss)):
			ts_name = obs_tss[i]
			ts_fn = ots_ts_fn[i]

			# Get timeseries
			(ts, val) = u_metrics.timeseries(ts_name, metric=obs_metrics)

			# On 1 onwards, strip the heading item, because it matches
			# the 'current' and might look like a spike in the plot
			if i > 0:
				ts = ts[1:]
				val[0] = val[0][1:]

			# Concatenate time series and values
			ts_values = list(reversed(val[0])) + ts_values
			ts_legends = map(lambda x: ts_fn(int(float(x))), reversed(ts)) + ts_legends
			ts_size.insert(0, len(ts) )

		# Split timeseries to show them in different colors
		ranges = []
		range_start = 0
		for c in ts_size:

			# Create empty array
			rng = [None] * len(ts_values)

			# Copy portion
			plus_1 = 1
			if range_start+c >= len(ts_values):
				plus_1 = 0
			rng[range_start:range_start+c+plus_1] = ts_values[range_start:range_start+c+plus_1]

			# Go to next item
			range_start += c

			# Store on ranges
			ranges.append(rng)

		# Add holes every 'nth' item
		for i in range(0, len(ts_values), 2):
			ts_legends[i] = ""

		# Return values
		return {
			'plot': {
				'labels': ts_legends,
				'series': ranges
			}
		}

	else:
		raise APIError("Unknown command")
