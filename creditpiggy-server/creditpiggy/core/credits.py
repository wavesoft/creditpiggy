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

from creditpiggy.core.achievements import check_achievements, check_campaign_achievements
from creditpiggy.core.models import ProjectUserRole, Campaign, CampaignUserCredit, CreditSlot

############################################################
# Helper functions
############################################################

def import_to_campaigns( slot, user, website ):
	"""
	Import specified metrics to relevant website campaigns
	"""

	# Access metrics
	m_slot = slot.metrics()

	# Get credits and metrics
	slot_credits = slot.credits
	slot_metrics = m_slot.counters()

	# Update all relevant campaigns running for the project
	campaigns = Campaign.ofWebsite( website, active=True, expired=False )
	for campaign in campaigns:

		# Update campaign metrics
		m_campaign = campaign.metrics()
		m_campaign.cincr("credits", slot_credits)		# Update campaign credits
		m_campaign.cincr("slots/completed", 1)			# Update completed slot counter
		m_campaign.cincr( slot_metrics )				# Update slot metrics

		# Update credits histogram
		m_campaign.hadd( "credits", slot_credits, 1 )	# Update the distribution of credits in the campaign

		# Find the campaign/user link
		(cu_credits, created) = CampaignUserCredit.objects.get_or_create(
				user=user, campaign=campaign
			)

		# The first time the user joins a campaign, increment
		# participation counters
		if created:	

			# Update user metrics
			m_owner = user.metrics()
			m_owner.cincr("participate/campaigns", 1) # Update campaigns participated

			# Update project metrics
			m_campaign.cincr("participate/users", 1)	# Update users participated

		# Stack machine credits
		cu_credits.credits += slot_credits
		cu_credits.save()

		# Update project-credits metrics
		m_cu = cu_credits.metrics()
		m_cu.cincr("credits", slot_credits)		# Update credits on the project/user
		m_cu.cincr("slots/completed", 1)		# Update completed slot counter
		m_cu.cincr( slot_metrics )				# Squash all counters of slot to the project/user

		# Check campaign achievements
		check_campaign_achievements( campaign )

def import_to_project( slot ):
	"""
	Import slot metrics to the project and relevant campaigns
	"""

	# Access metrics
	m_slot = slot.metrics()

	# Get credits and metrics
	slot_credits = slot.credits
	slot_metrics = m_slot.counters()

	# This is never the chance, but just in case
	if slot.project is None:
		return

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("credits", slot_credits)		# Update machine credits
	m_project.cincr("slots/completed", 1)			# Update completed slot counter
	m_project.cincr( slot_metrics )					# Update slot metrics

	# Update credits histogram
	m_project.hadd( "credits", slot_credits, 1 )	# Update the distribution of credits in the project

def import_to_user( slot, user ):
	"""
	Import machine counters to the owner
	"""

	# Access metrics
	m_slot = slot.metrics()

	# Get credits and metrics
	slot_credits = slot.credits
	slot_metrics = m_slot.counters()

	# This is never the chance, but just in case
	if slot.machine is None:
		return

	# Getch owner metrics
	m_owner = user.metrics()
	m_owner.cincr("credits", slot_credits)			# Update user credits
	m_owner.cincr("slots/completed", 1)				# Update completed slot counter
	m_owner.cincr( slot_metrics )					# Update slot metrics

def import_to_machine( slot ):
	"""
	Import slot metrics to the owned machine
	"""

	# This is never the chance, but just in case
	if slot.machine is None:
		return
	if slot.machine.owner is None:
		return

	# The machine record is just the link between
	# the slot and the user, so we don't need to store
	# anything in the machine record itself. All pending
	# data are waiting on each individual slot-machine record.

	# Import metrics to the campaign
	import_to_campaigns( slot, slot.machine.owner, slot.machine.website )

	# Forward metrics to the user
	import_to_user( slot, slot.machine.owner )


def import_to_users_project( slot, user ):
	"""
	Import slot counters to the user's project
	"""

	# Access metrics
	m_slot = slot.metrics()

	# Get credits and metrics
	slot_credits = slot.credits
	slot_metrics = m_slot.counters()

	# This is never the chance, but just in case
	if slot.project is None:
		return

	# Find the project/owner link
	(pu_credits, created) = ProjectUserRole.objects.get_or_create(
			user=user, project=slot.project, defaults=dict(
				role=ProjectUserRole.MEMBER
			)
		)

	# The first time the user joins a project, increment
	# participation counters
	if created:	

		# Update user metrics
		m_owner = user.metrics()
		m_owner.cincr("participate/projects", 1) # Update projects participated

		# Update project metrics
		m_project = slot.project.metrics()
		m_project.cincr("participate/users", 1)	# Update users participated

	# Stack machine credits
	pu_credits.credits += slot_credits
	pu_credits.save()

	# Update project-credits metrics
	m_pu = pu_credits.metrics()
	m_pu.cincr("credits", slot_credits)		# Update credits on the project/user
	m_pu.cincr("slots/completed", 1)		# Update completed slot counter
	m_pu.cincr( slot_metrics )				# Squash all counters of slot to the project/user

	# Check user achievements in this project
	check_achievements( pu_credits )

def import_machine_slots( machine ):
	"""
	Process all the pending slots linked to this machine
	"""

	# Lookup relevant slots
	print ">>> Importing credits of machine %s" % machine.uuid
	for slot in CreditSlot.objects.filter( machine=machine ):

		# Import slot details to the machine
		print ">>> Import slot %s to it's machine" % slot.uuid
		import_to_machine( slot )
		# Import slot metrics to user/project
		print ">>> Import slot %s to user %s" % (slot.uuid, str(machine.owner))
		import_to_users_project( slot, machine.owner )
		# The slot is now consumed
		print ">>> Delete slot"
		slot.delete()

############################################################
# Slot management
############################################################

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

	# The moment a slot is claimed, the only think we 
	# have for sure is the project, since the slot was
	# allocated for a particular project. So, before
	# anything else, import counters to the project.
	import_to_project( slot )

	# Link this slot to the machine
	slotDirty = False
	if slot.machine != machine:

		# Update and mark slot as dirty, because
		# we might just delete it by the end instead
		# of saving it.
		slot.machine = machine
		slotDirty = True

	# It's not possible to know the user/project relation
	# up to the point the machine is claimed by a user.
	#
	# Therefore we are going to wait for an owner before
	# we flush the slot contents.
	#
	if not machine.owner is None:

		# Import slot metrics to machine. 
		# Keep in mind that since the machine is just the link
		# between the computing node and the user, this actually
		# just updates the user record 
		import_to_machine( slot )

		# Import slot metrics to user/project
		import_to_users_project( slot, machine.owner )

		# The slot is now consumed
		slot.delete()
		return

	# If slot is dirty, save now
	if slotDirty:
		slot.save()

def discard_slot( slot, reason ):
	"""
	The slot 'slot' was discarded for reason 'reason'
	"""

	# Update project metrics
	m_project = slot.project.metrics()
	m_project.cincr("slots/discarded", 1)			# Update discarded slot counter on the project

	# Update reason stats
	m_project.hadd( "discard_reason", reason, 1 )	# Update the histogram distribution

