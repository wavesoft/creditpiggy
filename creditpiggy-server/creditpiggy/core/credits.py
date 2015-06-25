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

from creditpiggy.core.achievements import check_achievements
from creditpiggy.core.models import ProjectUserRole, Campaign

def alloc_slot( slot ):
	"""
	The slot 'slot' was allocated to the project
	"""

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("slots/allocated", 1)			# Update allocated slot counter

	# Update all relevant campaigns running for the project
	campaigns = Campaign.ofProject( slot.project )
	for campaign in campaigns:

		# Update campaign metrics
		m_campaign = campaign.metrics()
		m_project.cincr("slots/allocated", 1)		# Update allocated slot counter

def claim_slot( slot, machine ):
	"""
	The slot 'slot' was claimed by the machine 'machine'
	"""

	# Get credits to give to the user
	credits = slot.credits

	# Get slot metrics
	m_slot = slot.metrics()
	slot_metrics = m_slot.counters()

	# Update machine metrics
	m_machine = machine.metrics()
	m_machine.cincr("credits", credits)				# Update credits on the machine
	m_machine.cincr( slot_metrics )					# Squash all counters of slot to the machine

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("credits", credits)				# Update credits on the project
	m_project.cincr( slot_metrics )					# Squash all counters of slot to the project
	m_project.cincr("slots/completed", 1)			# Update completed slot counter

	# Update credits histogram
	m_project.hadd( "credits", credits, 1 )			# Update the histogram distribution

	# Update all relevant campaigns running for the project
	campaigns = Campaign.ofProject( slot.project )
	for campaign in campaigns:

		# Update campaign metrics
		m_campaign = campaign.metrics()
		m_campaign.cincr("credits", credits)	# Update credits on the project
		m_campaign.cincr( slot_metrics )		# Squash all counters of slot to the project
		m_campaign.cincr("slots/completed", 1)	# Update completed slot counter

	# Check if there is a user associated with this machine
	if not machine.owner is None:

		# Get and reset machine counters
		machine_counters = m_machine.counters()
		m_machine.creset()

		# Getch machine metrics
		m_owner = machine.owner.metrics()
		m_owner.cincr( machine_counters )			# Squash all macine counters to the owner

		# Find the project/owner link
		(pu_credits, created) = ProjectUserRole.objects.get_or_create(
				user=machine.owner, project=slot.project, defaults=dict(
					role=ProjectUserRole.MEMBER
				)
			)

		# Stack machine credits
		pu_credits.credits += int(machine_counters["credits"])
		pu_credits.save()

		# Update project-credits metrics
		m_pu = pu_credits.metrics()
		m_pu.cincr( machine_counters )				# Squash all macine counters to project-user link

		# Contribute to active campaigns
		for campaign in campaigns:

			# Update the project/owner link
			(cu_credits, created) = CampaignUserCredit.objects.get_or_create(
					user=machine.owner, campaign=campaign
				)

			# Stack machine credits
			cu_credits.credits += int(machine_counters["credits"])
			cu_credits.save()

			# Update project-credits metrics
			m_cu = cu_credits.metrics()
			m_cu.cincr( machine_counters )			# Squash all macine counters to project-campaign link

		# Check and grant user achievements on the project
		check_achievements( pu_credits )

def discard_slot( slot, reason ):
	"""
	The slot 'slot' was discarded for reason 'reason'
	"""

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("slots/discarded", 1)			# Update discarded slot counter on the project

	# Update reason stats
	m_project.hadd( "discard_reason", reason, 1 )	# Update the histogram distribution

	# Update all relevant campaigns running for the project
	campaigns = Campaign.ofProject( slot.project, active=True )
	for campaign in campaigns:

		# Update campaign metrics
		m_campaign = campaign.metrics()
		m_campaign.cincr("slots/discarded", 1)		# Update discarded slot counter on the project

