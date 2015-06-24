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

import locale
import time
import pytz

from django.conf import settings
from django import template
from datetime import datetime

# Get registry
register = template.Library()

@register.filter(name='get_metrics')
def get_metrics(value):
	"""
	Get the achievement metric
	"""
	return value.getMetrics().iteritems()

@register.filter(name='thousands')
def thousands(value): # Add ',' on thousands
	"""
	Divide thousand triplets
	"""

	# Get value
	try:
		if '.' in str(value):
			v = float(value)
		else:
			v = int(value)
	except ValueError:
		v = 0

	# Format value
	locale.setlocale(locale.LC_ALL, 'en_US')
	return str(locale.format("%d", v, grouping=True))

@register.filter(name='timestamp')
def timestamp(value): # Only one argument.
	"""
	Unix timestamp to timezoned date
	"""

	# Normalize date
	local_tz = pytz.timezone( settings.TIME_ZONE ) 
	utc_dt = datetime.utcfromtimestamp(int(value)).replace(tzinfo=pytz.utc)
	local_dt = local_tz.normalize(utc_dt.astimezone(local_tz))

	# Stringify and return
	return str(local_dt)

@register.filter(name='time_delta')
def time_delta(value): # Only one argument.
	"""
	Return time delta
	"""

	t_sec = int(value) - int(time.time())
	t_min = 0
	t_hour = 0

	if t_sec >= 60:
		t_min = int(t_sec / 60)
		t_sec = t_sec % 60

		if t_min >= 60:
			t_hour = int(t_min / 60)
			t_min = t_min % 60

	return "%i:%02i:%02i" % (t_hour, t_min, t_sec)

