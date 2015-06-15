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

import pytz
from django.utils import timezone

class TimezoneMiddleware(object):
	def process_request(self, request):
		tzname = request.session.get('django_timezone')

		# Apply user's timezone
		if request.user.is_authenticated():
			timezone.activate(pytz.timezone(request.user.timezone))

		# Otherwise, detect from session
		elif tzname:
			timezone.activate(pytz.timezone(tzname))

		else:
			timezone.deactivate()
