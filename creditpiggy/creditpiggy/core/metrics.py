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
from creditpiggy.core.housekeeping import HousekeepingTask, periodical

class MetricsHousekeeping(HousekeepingTask):
	"""
	Metrics housekeeping class
	"""

	@periodical(hours=1, priority=1)
	def rotate_hourly(self):
		"""
		Rotate hourly data
		"""
		print "-- Periodical: Hourly"

	@periodical(days=1, priority=2)
	def rotate_daily(self):
		"""
		Rotate daily data
		"""
		print "-- Periodical: Daily"

	@periodical(days=7, priority=3)
	def rotate_weekly(self):
		"""
		Rotate weekly data
		"""
		print "-- Periodical: Weekly"

	@periodical(days=28, priority=4)
	def rotate_monthly(self):
		"""
		Rotate monthly (4-week) data
		"""
		print "-- Periodical: Monthly"

	@periodical(days=364, priority=5)
	def rotate_yearly(self):
		"""
		Rotate yearly (13 x 4-week months) data
		"""
		print "-- Periodical: Yearly"

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

	def delete_instance(self):
		"""
		Delete instance metrics
		"""

		# Delete within a pipeline
		pipe = self.redis.pipeline()

		# Remove from housekeeping
		pipe.srem( settings.REDIS_KEYS_PREFIX + "metrics/housekeeping", self.namespace )
		pipe.delete( "%s/history" % self.namespace )
		pipe.delete( "%s/counters" % self.namespace )
		pipe.delete( "%s/meta" % self.namespace )

		# Run pipeline
		pipe.execute()

	def counters(self):
		"""
		Return all counters
		"""

		# Get all counters
		value = self.redis.hgetall( "%s/counters" % self.namespace )
		if not value:
			return {}

		# Create dict with the values
		return value

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

	def incr(self, metric, value=1):
		"""
		Increment a counter
		"""

		# If metric is a dictionary, update multiple
		if isinstance(metric, dict):

			# Increment each key of dict
			pipe = self.redis.pipeline()

			# Increment <k> by <v>
			for k,v in metric.iteritems():
				self.redis.hincrby( "%s/counters" % self.namespace, k, int(v) )

			# Run pipeline
			pipe.execute()

		else:

			# Increment metric by <value>
			self.redis.hincrby( "%s/counters" % self.namespace, metric, int(value) )

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

	def metrics_ns(self):
		"""
		Return the metrics namespace for the current model instance
		"""

		# Get FQN of the base class
		fqn = self.__module__ + "." + self.__class__.__name__

		# Get the name of the primary key field name
		pkf = self._meta.pk.name

		# Generate a unique for this entry metrics tracking ID
		return "metrics/%s/%s" % (fqn, str(getattr(self, pkf)))

	def delete_metrics(self):
		"""
		Delete metrics associated with this model
		"""

		# Delete metrics instance
		self.metrics().delete_instance()

	def metrics(self):
		"""
		Return the metrics tracking class
		"""
		
		# Create a metrics instance only once
		if not hasattr(self,'_metricsInstance'):
			self._metricsInstance = Metrics( self.metrics_ns() )

		# Return an metrics class within the model's namespace
		return self._metricsInstance

