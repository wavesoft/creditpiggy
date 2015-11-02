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

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q

from creditpiggy.core.models import CreditSlot, ComputingUnit, PiggyUser, Referral, new_token
from creditpiggy.core.credits import import_machine_slots
from creditpiggy.core.achievements import check_personal_achievements

from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import allow_cors

##########################################
# Public API Calls
##########################################

@render_with_api(context="js.status")
@allow_cors()
def referrer(request, api="json"):
	"""
	Query details regarding a user, project or website
	"""

	return { }

