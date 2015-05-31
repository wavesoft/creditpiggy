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
import creditpiggy.core.credits as credits

from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt

from creditpiggy.core.models import CreditSlot
from creditpiggy.api.protocol import render_with_api, APIError
from creditpiggy.api.auth import require_project_auth


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

	# Get expire time (Default to 24h)
	expire_time = 1440
	if 'expire' in args:
		expire_time = int(args['expire'])

	# Set the slot expire time
	slot.expireTime = int(time.time()) + expire_time * 60

	# Save slot
	slot.save()

def _discard_slot(project, args):
	"""
	Discard slot (ex. because of an error)
	"""

	# Require 'slot' and 'machine'
	if not 'slot' in args:
		raise APIError("Missing 'slot' argument")

	# Get 'reason'
	reason = 'unspecified'
	if 'reason' in args:
		reason = args['reason']

	# Lookup slot
	slots = CreditSlot.objects.filter(uuid = args['slot'], project = project)
	if len(slots) == 0:
		raise APIError("Discarding non-existing slot: '%s' for project: '%s'" % (args['slot'], str(project)))

	# Get first slot
	slot = slots[0]

	# The slot was discarded
	credits.discard_slot( slot, reason )

	# Delete slot
	slot.delete()

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
	if (slot.credits is None):
		if 'credits' in args:
			slot.credits = int(args['credits'])
		else:
			# Forgot to define credits? Assume the fact that the job
			# was claimed is succicient enough to give 1 credit.
			slot.credits = 1

	# Wrap credits in bounds if existing
	if not (slot.minBound is None) and (slot.credits < slot.minBound):
		slot.credits = slot.minBound
	if not (slot.maxBound is None) and (slot.credits > slot.maxBound):
		slot.credits = slot.maxBound

	# Claim this slot by the specified machine
	credits.claim_slot( slot, machine )

	# Delete slot
	slot.delete()

def _counters_slot(project, args):
	"""
	Update counters of the specified credit slot
	"""

	# Require 'slot' and 'machine'
	if not 'slot' in args:
		raise APIError("Missing 'slot' argument")

	# Lookup slot
	slots = CreditSlot.objects.filter(uuid = args['slot'], project = project)
	if len(slots) == 0:
		raise APIError("Updating counters in a non-existing slot: '%s' for project: '%s'" % (args['slot'], str(project)))

	# Get first slot
	slot = slots[0]

	# Update metrics
	metrics = slot.metrics()
	for k,v in args.iteritems():

		# Skip 'slot' argument
		if k == "slot":
			continue

		# Everything else is used as a counter
		metrics.incr( k, int(v) )

def _meta_slot(project, args):
	pass

##########################################
# Batch System API Commands
##########################################

@csrf_exempt
@render_with_api(context="batch.alloc")
@require_project_auth()
def slot_alloc(request, api):
	"""
	Allocate a slot
	"""

	# Allocate slot or raise APIErrors
	_alloc_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="batch.claim")
@require_project_auth()
def slot_claim(request, api):
	"""
	Claim a slot
	"""

	# Claim slot or raise APIErrors
	_claim_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="batch.discard")
@require_project_auth()
def slot_claim(request, api):
	"""
	Discard a slot
	"""

	# Claim slot or raise APIErrors
	_discard_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="batch.meta")
@require_project_auth()
def slot_meta(request, api):
	"""
	Define slot metadata
	"""

	# Update slot metadata or raise APIErrors
	_meta_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="batch.counters")
@require_project_auth()
def slot_counters(request, api):
	"""
	Append slot coutners
	"""

	# Update slot counters or raise APIErrors
	_counters_slot( request.project, request.proto.getAll() )

@csrf_exempt
@render_with_api(context="batch.bulk")
@require_project_auth()
def bulk_commands(request, api):
	"""
	Execute a command bulk, possibly sent by the CreditPiggy
	daemon in the application server.
	"""

	# Get commands
	commands = request.proto.getAll()

	# Handle 'alloc' commands in priority #1
	if 'alloc' in commands:

		# Satisfy all requests
		for args in commands['alloc']:
			_alloc_slot( request.project, args )

		# Delete alloc command
		del commands['alloc']

	# Handle 'counters' commands in priority #2
	if 'counters' in commands:

		# Satisfy all requests
		for args in commands['counters']:
			_alloc_slot( request.project, args )

		# Delete counters command
		del commands['counters']

	# Handle 'meta' commands in priority #3
	if 'meta' in commands:

		# Satisfy all requests
		for args in commands['meta']:
			_alloc_slot( request.project, args )

		# Delete meta command
		del commands['meta']

	# Handle 'discard' commands in priority #4
	if 'discard' in commands:

		# Satisfy all requests
		for args in commands['discard']:
			_alloc_slot( request.project, args )

		# Delete discard command
		del commands['discard']

	# Handle 'claim' commands in priority #5
	if 'claim' in commands:

		# Satisfy all requests
		for args in commands['claim']:
			_alloc_slot( request.project, args )

		# Delete claim command
		del commands['claim']

	# Everything else is invalid command
	if commands:
		# Unknown
		raise APIError("Unknown command '%s' in bulk set" % commands.keys()[0])

