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

from django.db import models
from django.conf import settings

from creditpiggy.core.redis import share_redis_connection
from creditpiggy.core.housekeeping import HousekeepingTask, periodical

class Metrics:
	"""
	Metrics management class
	"""

	def __init__(self, namespace, features):
		"""
		Create an instance of the metrics class
		"""

		# Get a connection to the REDIS server
		self.redis = share_redis_connection()

		# Keep a reference of the namespace to operate upon
		self.namespace = settings.REDIS_KEYS_PREFIX + namespace

		# Apply for housekeeping if we have features
		if features:

			# Register for housekeeping
			self.redis.sadd( settings.REDIS_KEYS_PREFIX + "metrics/housekeeping", self.namespace )

			# Create a features dict
			feature_dict = { }
			for k,v in features.iteritems():

				# Iterate over lists
				if isinstance(v, tuple) or isinstance(v, list):
					for feat in v:
						# Initialize feature
						if not feat in feature_dict:
							feature_dict[feat] = []

						# Include the variable
						feature_dict[feat].append(k)

				# Otherwise use single value
				else:
					# Initialize feature
					if not v in feature_dict:
						feature_dict[v] = []

					# Include the variable
					feature_dict[v].append(k)

			# Store what metrics belong in which features:
			# { 'feature': [ 'metric' ] }
			#
			self.redis.hmset( "%s/features" % self.namespace, feature_dict )


	def delete(self):
		"""
		Delete instance metrics
		"""

		# Get all keys under this namespace
		del_keys = self.redis.keys("%s*" % self.namespace)

		# Delete within a pipeline
		pipe = self.redis.pipeline()

		# Remove from housekeeping
		pipe.srem( settings.REDIS_KEYS_PREFIX + "metrics/housekeeping", self.namespace )

		# Remove all keys under this namespace
		for key in del_keys:
			pipe.delete(key)

		# Run pipeline
		pipe.execute()

	######################################
	# Counters
	######################################

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

	def cset(self, metric, value):
		"""
		Set a counter value
		"""
		# Increment metric by <value>
		self.redis.hset( "%s/counters" % self.namespace, metric, value )

	def creset(self):
		"""
		Reset all counters
		"""
		# Delete counters
		self.redis.delete( "%s/counters" % self.namespace )

	def cincr(self, metric, value=1):
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

	######################################
	# Histograms
	######################################

	def histograms(self):
		"""
		Return all histograms under this namespace
		"""

		# Find histograms
		h_keys = self.redis.keys("%s/histo/*" % self.namespace)

		# Create dictionary of histograms
		ans = {}
		for k in h_keys:

			# Get histogram
			parts = k.split("/histo/", 1)
			ans[parts[1]] = self.redis.hgetall( k )

		# Return them
		return ans

	def histogram(self, histogram):
		"""
		Return the histogram under the specified name
		"""

		# Get all histogram bins
		bins = self.redis.hgetall( "%s/histo/%s" % (self.namespace, histogram) )

		# Return them
		return bins

	def hadd(self, histogram, bin, value=1):
		"""
		Add value 'value' to histogram 'histogram's bin named 'bin'.

		This function does not take care of any binning process, you will need
		to perform this binning prior on calling this.
		"""

		# Update the histogram bin
		self.redis.hincrby(
				"%s/histo/%s" % (self.namespace, histogram), 
				str(bin), 
				int(value)
			)

class MetricsModelMixin(object):
	"""
	A metrics Mix-in that when merged with a model provides
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

	#: The features to apply on arbitrary metrics
	METRICS_FEATURES = None

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

	def delete(self):
		"""
		Delete metrics associated with this model
		"""

		# Delete metrics instance
		self.metrics().delete()

		# Fire the delete() in all the other superclasses of our mixin
		for base in self.__class__.__bases__:
			if (not base is MetricsModelMixin) and hasattr(base, 'delete'):
				base.delete(self)

	def metrics(self):
		"""
		Return the metrics tracking class
		"""

		# Create a metrics instance only once
		if not hasattr(self,'_metricsInstance'):
			self._metricsInstance = Metrics( self.metrics_ns(), self.__class__.METRICS_FEATURES )

		# Return an metrics class within the model's namespace
		return self._metricsInstance


class MetricFeaturesHousekeeping(HousekeepingTask):
	"""
	Housekeeping for the metric features
	"""

	def __init__(self):
		"""
		Initialize the housekeeping class
		"""

		# Get a connection to the REDIS server
		self.redis = share_redis_connection()

		# Enumerate all the housekeeping namespaces
		self.namespaces = list(self.redis.smembers( settings.REDIS_KEYS_PREFIX + "metrics/housekeeping" ))

		# Fetch all the namespace features in a pipeline, in addition
		# with the counter values, since we are going to probe them later
		# one way or another (since they are participating in housekeeping)
		p = self.redis.pipeline()
		for ns in self.namespaces:
			p.hgetall( "%s/features" % ns )
			p.hgetall( "%s/counters" % ns )
		ans = p.execute()

		# Process features
		i = -1
		self.features = { }
		for ft in ans[0::2]:
			i += 1
			ns = self.namespaces[i]

			# Process metrics in the appropriate features
			for feat, metric in ft.iteritems():

				# Create feature if missing
				if not feat in self.features:
					self.features[feat] = {}
				if not ns in self.features[feat]:
					self.features[feat][ns] = []

				# Store metrics in namespace
				self.features[feat][ns].append( metric )

		# Process counters
		i = -1
		self.counters = { }
		for cnt in ans[1::2]:
			i += 1
			self.counters[self.namespaces[i]] = cnt

	def merge(self, src, dst):
		"""
		Merge all counters from src to dst
		"""
		for k,v in src.iteritems():

			# Create missing keys
			if not k in dst:
				dst[k] = 0

			# Add values
			dst[k] = int(dst[k]) + int(v)

		# Return dst
		return dst

	def ring_rotate(self, pipeline, values, key, trim):
		"""
		Insert an item in the ring and trim excess items
		"""

		# Insert values and timestamp in the list
		pipeline.lpush( "%s/val" % key, json.dumps(values) )
		pipeline.lpush( "%s/ts" % key, time.time() )

		# Chomp list
		pipeline.ltrim( "%s/val" % key, 0, trim )
		pipeline.ltrim( "%s/ts" % key, 0, trim )

	@periodical(hours=1, priority=1)
	def rotate_hourly(self):
		"""
		Rotate hourly data
		"""

		# Handle all metrics with feature 'ts_hourly'
		if not 'ts_hourly' in self.features:
			return

		# Create a redis pipeline since all the operations
		# are write-only
		pipeline = self.redis.pipeline()

		# Perform operations
		for ns, metrics in self.features['ts_hourly'].iteritems():

			# Get only the specified metrics from the counters
			c = self.counters[ns]
			metrics = dict([ c[x] for x in list(set(ns.keys()) & set(metrics)) ])

			# Manage ring rotation
			self.ring_rotate(
				pipeline,				# Use the allocated pipeline
				metrics,				# Put values of counter
				"%s/ts/hourly" % ns,	# In that ring
				24						# Having that many items at maximum
				)

		# Execute pipeline
		pipeline.execute()

	@periodical(days=1, priority=2)
	def rotate_daily(self):
		"""
		Rotate daily data
		"""

		# Handle all metrics with feature 'ts_daily'
		if not 'ts_daily' in self.features:
			return

		# Create a redis pipeline since all the operations
		# are write-only
		pipeline = self.redis.pipeline()

		# Perform operations
		for ns, metrics in self.features['ts_daily'].iteritems():

			# Get only the specified metrics from the counters
			c = self.counters[ns]
			metrics = dict([ c[x] for x in list(set(ns.keys()) & set(metrics)) ])

			# Manage ring rotation
			self.ring_rotate(
				pipeline,				# Use the allocated pipeline
				metrics,				# Put values of counter
				"%s/ts/daily" % ns,		# In that ring
				7						# Having that many items at maximum
				)

		# Execute pipeline
		pipeline.execute()

	@periodical(days=7, priority=3)
	def rotate_weekly(self):
		"""
		Rotate weekly data
		"""

		# Handle all metrics with feature 'ts_weekly'
		if not 'ts_weekly' in self.features:
			return

		# Create a redis pipeline since all the operations
		# are write-only
		pipeline = self.redis.pipeline()

		# Perform operations
		for ns, metrics in self.features['ts_weekly'].iteritems():

			# Get only the specified metrics from the counters
			c = self.counters[ns]
			metrics = dict([ c[x] for x in list(set(ns.keys()) & set(metrics)) ])

			# Manage ring rotation
			self.ring_rotate(
				pipeline,				# Use the allocated pipeline
				metrics,				# Put values of counter
				"%s/ts/weekly" % ns,	# In that ring
				4						# Having that many items at maximum
				)

		# Execute pipeline
		pipeline.execute()

	@periodical(days=28, priority=4)
	def rotate_monthly(self):
		"""
		Rotate monthly (4-week) data
		"""

		# Handle all metrics with feature 'ts_monthly'
		if not 'ts_monthly' in self.features:
			return

		# Create a redis pipeline since all the operations
		# are write-only
		pipeline = self.redis.pipeline()

		# Perform operations
		for ns, metrics in self.features['ts_monthly'].iteritems():

			# Get only the specified metrics from the counters
			c = self.counters[ns]
			metrics = dict([ c[x] for x in list(set(ns.keys()) & set(metrics)) ])

			# Manage ring rotation
			self.ring_rotate(
				pipeline,				# Use the allocated pipeline
				metrics,				# Put values of counter
				"%s/ts/monthly" % ns,	# In that ring
				13						# Having that many items at maximum
				)

		# Execute pipeline
		pipeline.execute()

	@periodical(days=364, priority=5)
	def rotate_yearly(self):
		"""
		Rotate yearly (13 x 4-week months) data
		"""

		# Handle all metrics with feature 'ts_yearly'
		if not 'ts_yearly' in self.features:
			return

		# Create a redis pipeline since all the operations
		# are write-only
		pipeline = self.redis.pipeline()

		# Perform operations
		for ns, metrics in self.features['ts_yearly'].iteritems():

			# Get only the specified metrics from the counters
			c = self.counters[ns]
			metrics = dict([ c[x] for x in list(set(ns.keys()) & set(metrics)) ])

			# Manage ring rotation
			self.ring_rotate(
				pipeline,				# Use the allocated pipeline
				metrics,				# Put values of counter
				"%s/ts/yearly" % ns,	# In that ring
				5						# Having that many items at maximum
				)

		# Execute pipeline
		pipeline.execute()

