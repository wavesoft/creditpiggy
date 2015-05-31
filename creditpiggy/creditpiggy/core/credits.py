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

from creditpiggy.core.models import ProjectUserCredit

def alloc_slot( slot ):
	"""
	The slot 'slot' was allocated to the project
	"""

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("slots/allocated", 1)			# Update allocated slot counter

def claim_slot( slot, machine ):
	"""
	The slot 'slot' was claimed by the machine 'machine'
	"""

	# Get credits to give to the user
	credits = slot.credits

	# Get machine metrics
	m_machine = machine.metrics()
	m_machine.cincr("credits", credits)				# Update credits on the machine
	m_machine.cincr( slot.metrics().counters() )	# Squash all counters of slot to the machine

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("credits", credits)				# Update credits on the project
	m_project.cincr( slot.metrics().counters() )	# Squash all counters of slot to the project
	m_project.cincr("slots/completed", 1)			# Update completed slot counter

	# Update reason stats
	m_project.hadd( "credits", credits, 1 )			# Update the histogram distribution

	# Check if there is a user associated with this machine
	if not machine.owner is None:

		m_owner = machine.owner.metrics()
		m_owner.cincr("credits", credits) 			# Update credits on the user
		m_owner.cincr( slot.metrics().counters() )	# Squash all counters of slot to the owner

		# Find the project/owner link
		pu_credits = ProjectUserCredit.get_or_create(
				user=machine.owner, project=slot.project
			)

		# Get owner credits
		pu_credits.credits = m_owner.counter("credits")
		pu_credits.save()


def discard_slot( slot, reason ):
	"""
	The slot 'slot' was discarded for reason 'reason'
	"""

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("slots/discarded", 1)			# Update discarded slot counter on the project

	# Update reason stats
	m_project.hadd( "discard_reason", reason, 1 )	# Update the histogram distribution

