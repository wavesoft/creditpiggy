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

from __future__ import absolute_import

from django.conf import settings
import redis

#: The shared REDIS connection pool
shared_pool = None

def share_redis_connection():
	"""
	Get a shared REDIS connection by using a reusable, common redis pool
	"""

	# Initialize the shared_pool if not yet initialized
	global shared_pool
	if not shared_pool:
		shared_pool = redis.ConnectionPool( host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB )

	# Return a redis pool instance
	return redis.StrictRedis(connection_pool=shared_pool)

