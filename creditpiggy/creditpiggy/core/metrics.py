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


from django.db import models
from django.conf import settings

from creditpiggy.core.redis import share_redis_connection

class MetricsHousekeeping:
	"""
	Metrics housekeeping class
	"""

class Metrics:
	"""
	Metrics management class
	"""

	def __init__(self, namespace):
		"""
		Create an instance of the metrics class
		"""

		# Get a connection to the REDIS server
		self.redis = share_redis_connection()

		# Keep a reference of the namespace to operate upon
		self.namespace = settings.REDIS_KEYS_PREFIX + namespace

		# Keep the occupied namespace in redis for housekeeping
		self.redis.sadd( settings.REDIS_KEYS_PREFIX + "metrics/housekeeping", self.namespace )

	def counter(self, metric, default=None):
		"""
		Return the value of a field counter
		"""

		# Get counter value
		value = self.redis.hget( "%s/counters" % self.namespace, metric )

		# If missing return default
		if value is None:
			return default
		return value

	def inc(self, metric, value=1):
		"""
		Increment a counter
		"""
		# Increment metric by <value>
		self.redis.hincrby( "%s/counters" % self.namespace, metric, value )

	def set(self, metric, value):
		"""
		Set a counter value
		"""
		# Increment metric by <value>
		self.redis.hset( "%s/counters" % self.namespace, metric, value )

class MetricsModelMixin(object):
	"""
	An metrics Mix-in that when merged with a model provides
	a layer of metrics on it.

	The metrics layer provides the interface to timeseries analysis,
	trend calculation and other nice features in the most efficient
	manner possible.

	The data are stored in two locations:
	
	- Actively processed in a REDIS database
	- Periodically snapshotted into the model

	This way, if for any reason we loose the REDIS reflection, the data
	can be synced back to the database using the model snapshot.
	"""

	#: The snapshot of the metrics data
	#: (Uncomment this when the reflection is actually implemented)
	#metricsSnapshotData = models.TextField(null=True, default=None)
	#metricsSnapshotTime = models.IntegerField(null=True, default=None)

	def metrics_key(self):
		"""
		Return the metrics key for the base model
		"""

		# Get FQN of the base class
		fqn = self.__module__ + "." + self.__class__.__name__

		# Get the name of the primary key field name
		pkf = self._meta.pk.name

		# Generate a unique for this entry metrics tracking ID
		return "metrics/%s/%s" % (fqn, str(getattr(self, pkf)))

	def metrics(self):
		"""
		Return the metrics tracking class
		"""
		
		# Return an metrics class within the model's namespace
		return Metrics( self.metrics_key() )

