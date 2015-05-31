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

def claim_slot( slot, machine ):
	"""
	Claim slot 'slot' by the machine 'machine'
	"""

	# Get credits to add
	credits = slot.credits

	# Update credits on the machine
	machine.metrics().incr("credits", credits)
	# Squash all counters of slot to the machine
	machine.metrics().incr( slot.metrics().counters() )

	# Update credits on the project
	slot.project.metrics().incr("credits", credits)

	# Check if there is a user associated with this machine
	if not machine.owner is None:

		# Update credits on the user
		machine.owner.metrics().incr("credits", credits)
		# Squash all counters of slot to the owner
		machine.owner.metrics().incr( slot.metrics().counters() )

