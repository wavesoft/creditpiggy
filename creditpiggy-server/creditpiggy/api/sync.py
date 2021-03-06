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

import json
import time

from creditpiggy.core.redis import share_redis_connection
from creditpiggy.core.housekeeping import HousekeepingTask, periodical

class OfflineSync(HousekeepingTask):
	"""
	Apply slot updates to the respective accounts. This is used
	to throttle the infcoming requests and to optimize the api performance.
	"""

	def __init__(self):
		"""
		Initialize the offline synchronization class
		"""

		# Get a connection to the REDIS server
		self.redis = share_redis_connection()

	@periodical(minutes=1)
	def sync_task(self):
		"""
		Run the synchronization task every minute
		"""

		# Get all pending tasks
		
