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

from creditpiggy.core.models import CreditSlot
from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import require_project_auth

from creditpiggy.api.credits import claim_slot

from django.views.decorators.csrf import csrf_exempt


def _alloc_slot(project, args):
	"""
	Implement the slot allocation
	"""

	# Require 'slot'
	if not 'slot' in args:
		raise APIError("Missing 'slot' argument")

	# Create a credit slot
	slot = CreditSlot(
		uuid=args['slot'],
		project=project
		)

	# Check for credits or min/max
	if 'credits' in args:
		slot.credits = int(args['credits'])
	else:
		if 'min' in args:
			slot.minBound = int(args['min']) 
		if 'max' in args:
			slot.maxBound = int(args['max']) 

	# Save slot
	slot.save()

def _claim_slot(project, args):
	"""
	Claim a slot to the project
	"""

	# Require 'slot' and 'machine'
	if not 'slot' in args:
		raise APIError("Missing 'slot' argument")
	if not 'machine' in args:
		raise APIError("Missing 'machine' argument")

	# Lookup slot
	slots = CreditSlot.objects.filter(uuid = args['slot'], project = project)
	if len(slots) == 0:
		raise APIError("Claiming non-existing slot: '%s' for project: '%s'" % (args['slot'], str(project)))

	# Get first slot
	slot = slots[0]

	# Lookup or create relevant machine
	machine = ComputingUnit.objects.get_or_create(uuid = args['machine'])

	# If slot does not have credits, but we do have
	# credits specified in the arguments, apply them now
	if (slot.credits is None) and 'credits' in args:
		slot.credits = int(args['credits'])

	# Wrap credits in bounds if existing
	if not (slot.minBound is None) and (slot.credits < slot.minBound):
		slot.credits = slot.minBound
	if not (slot.maxBound is None) and (slot.credits > slot.maxBound):
		slot.credits = slot.maxBound

	# Claim this slot by the specified machine
	claim_slot( slot, machine )

def _counters_slot(project, args):

def _meta_slot(project, args):


@csrf_exempt
@render_with_api(context="project.alloc")
@require_project_auth()
def slot_alloc(request, api):
	"""
	Allocate a slot
	"""

	# Allocate slot or raise APIErrors
	_alloc_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="project.claim")
@require_project_auth()
def slot_claim(request, api):
	"""
	Claim a slot
	"""
	return { }

@csrf_exempt
@render_with_api(context="project.meta")
@require_project_auth()
def slot_meta(request, api):
	"""
	Define slot metadata
	"""
	return { }

@csrf_exempt
@render_with_api(context="project.counters")
@require_project_auth()
def slot_counters(request, api):
	"""
	Append slot coutners
	"""
	return { }

@csrf_exempt
@render_with_api(context="project.bulk")
@require_project_auth()
def bulk_commands(request, api):
	"""
	Execute a bulk of commands
	"""

	# Get commands
	commands = request.proto.getAll()

	# Handle 'alloc' commands in priority
	if 'alloc' in commands:

		# Satisfy all allocations
		for args in commands['alloc']:
			_alloc_slot( request.project, args )

		# Delete alloc command
		del commands['alloc']

	# Handle rest of the commands
	for cmd, cmdlist in commands.iteritems():

		if cmd == "claim":
			# Multiple claims
			for args in cmdlist:
				_claim_slot( request.project, args )

		elif cmd == "counters":
			# Multiple counters update
			for args in cmdlist:
				_counters_slot( request.project, args )

		elif cmd == "meta":
			# Multiple metadata update
			for args in cmdlist:
				_meta_slot( request.project, args )

