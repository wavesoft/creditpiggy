#!/usr/bin/env python
################################################################
# CreditPiggy - A Community Credit Management System
# Copyright (C) 2013 Ioannis Charalampidis
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

import os
import socket

#: The default CreditPiggy endpoint
_cpapi_endpoint = (2, "/var/run/creditapi.socket")

def cpapi_setup(server_endpoint, credentials=None):
	"""
	Setup CreditPiggy API to the specified server endpoint.
	The endpoint can be one of:

	- API URL of the CreditPiggy server
	- Path to a unix socket
	- Host:port configuration for a UDP socket
	"""

	# Process according to type
	if "://" in server_endpoint:
		# 1) URL
		_cpapi_endpoint = (1, server_endpoint)
	elif os.path.exists(server_endpoint) and not os.path.isfile(server_endpoint) and not os.path.isdir(server_endpoint):
		# 2) UNIX socket
		_cpapi_endpoint = (2, server_endpoint)
	elif ":" in server_endpoint:
		# 3) Network endpoint
		parts = server_endpoint.split(":")
		_cpapi_endpoint = (3, parts[0], int(parts[1]))
	else:
		# Raise a value error
		raise ValueError("Unrecognised server endpoint")

def _cpapi_command(command, args={}):
	"""
	Send a CPAPI command
	"""

	# Open socket according to type
	if _cpapi_endpoint[0] == 1:
		# 1) URL
		return

	elif _cpapi_endpoint[0] == 2:
		# 2) UNIX Socket

		# Open socket
		sock = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
		# Connect to endpoint
		sock.connect( _cpapi_endpoint[1] )

	elif _cpapi_endpoint[0] == 2:
		# 3) TCP Socket

		# Open socket
		sock = socket.socket( socket.AF_UNIX, socket.SOCK_STREAM )
		# Connect to endpoint
		sock.connect(( _cpapi_endpoint[1], _cpapi_endpoint[2] ))

	# Build command
	cmd = command
	for k,v in args.iteritems():
		cmd += ",%s=%s" % (k,v)

	# Send command & check for errors
	s_len = sock.send(cmd)
	if s_len != len(cmd):
		raise IOError("Unable to send a CreditPiggy API command")

	# Wait for response
	ans = sock.recv(4)
	if ans != "OK":
		raise IOError("Server could not process command '%s'" % command)

	# Close
	sock.close()

def cpapi_alloc(slot_id, min=None, max=None, credits=None, expire=None):
	"""
	Allocate the specified slot_id as a valid slot ID for the
	current project, with the specified credit range or fixed
	credit allocation.
	"""

	# Prepare arguments
	args = { "slot": slot_id }
	if not credits is None:
		args["credits"] = credits
	else:
		if not min is None:
			args["min"] = min
		if not max is None:
			args["max"] = max
	if not expire is None:
		args['expire'] = expire

	# Send command
	_cpapi_command("alloc", args)

def cpapi_claim(slot_id, machine_id, credits=None):
	"""
	Claim the credits allocated to slot_id by the machine_id.
	Optionally, if no credits were allocated at cpapi_alloc,
	specify the credits to give to the user.
	"""

	# Prepare arguments
	args = { "slot": slot_id, "machine": machine_id }
	if not credits is None:
		args["credits"] = credits

	# Send command
	_cpapi_command("claim", args)

def cpapi_discard(slot_id, reason=None):
	"""
	Discard the slot 'slot_id', optionally indicating the reason
	for doing so. Such reason might be 'expired', 'invalid', 'lost'
	etc.
	"""

	# Prepare arguments
	args = { "slot": slot_id }
	if not reason is None:
		args["reason"] = reason

	# Send command
	_cpapi_command("discard", args)

def cpapi_counters(slot_id, **kwargs):
	"""
	Set counters to the specified slot ID
	"""

	# Prepare arguments
	args = dict(kwargs)
	args['slot'] = slot_id

	# Send command
	_cpapi_command("counters", args)

def cpapi_meta(slot_id, **kwargs):
	"""
	Set metadata to the specified slot ID
	"""

	# Prepare arguments
	args = dict(kwargs)
	args['slot'] = slot_id

	# Send command
	_cpapi_command("meta", args)

