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

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

from creditpiggy.api.protocol import render_with_api, APIError

@login_required()
@render_with_api(context="profile.user.ajax", protocol="json")
def handle(request, cmd):
	"""
	Handle AJAX user request
	"""

	if cmd == "profile.set":

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
