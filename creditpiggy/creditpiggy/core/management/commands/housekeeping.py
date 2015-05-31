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

from django.core.management.base import BaseCommand, CommandError
from creditpiggy.core.housekeeping import HouseKeeping

# Get a logger
import logging
logger = logger.getLogger(__name__)

class Command(BaseCommand):
	help = 'Processes the housekeeping periodical tasks of the CreditPiggy server.'

	def add_arguments(self, parser):
		"""
		Register the --daemon argument
		"""
		parser.add_argument('--daemon', action='store_true')

	def handle(self, *args, **options):
		"""
		Execute the housekeeping command
		"""

		# Check daemon option
		if options['daemon']:
			logger.warn("Running as a demon")
		else:
			logger.warn("Running as a cron job")

		# Create a housekeeping class
		hk = HouseKeeping()

		# Run until there are no more dirty tasks
		while not hk.run():
			pass

