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
import logging
from django.core.management.base import BaseCommand, CommandError
from creditpiggy.core.housekeeping import HouseKeeping

# Get a logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
	help = 'Processes the housekeeping periodical tasks of the CreditPiggy server.'

	def add_arguments(self, parser):
		"""
		Register the --realtime argument
		"""
		parser.add_argument('--realtime', action='store_true', 
			help="Execute housekeeping tasks in realtime (stays in foreground)")

	def handle(self, *args, **options):
		"""
		Execute the housekeeping command
		"""

		# Create a housekeeping class
		hk = HouseKeeping()

		# Run infinitely if running as realtime
		while True:

			# Run until there are no more dirty tasks
			logger.info("Executing housekeeping tasks")
			while not hk.run():
				pass

			# Break if we are not running in real-time
			if not options['realtime']:
				break

			# Otherwise wait for a real-time event and
			# stay in the loop
			hk.waitEvent(0)
