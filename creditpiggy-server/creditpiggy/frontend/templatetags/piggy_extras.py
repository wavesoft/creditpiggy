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
from django import template

# Get registry
register = template.Library()

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

