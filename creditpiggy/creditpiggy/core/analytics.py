
from django.db import models
from creditpiggy.core.redis import share_redis_connection

class AnalyticsHousekeeping:
	"""
	Analytics housekeeping class
	"""

class Analytics:
	"""
	Analytics management class
	"""

	def __init__(self, namespace):
		"""
		Create an instance of the analytics class
		"""

		# Get a connection to the REDIS server
		self.redis = share_redis_connection()

		# Keep a reference of the namespace to operate upon
		self.namespace = namespace

class AnalyticsModelMixin(object):
	"""
	An analytics Mix-in that when merged with a model provides
	a layer of analytics on it.

	The analytics layer provides the interface to timeseries analysis,
	trend calculation and other nice features in the most efficient
	manner possible.

	The data are stored in two locations:
	
	- Actively processed in a REDIS database
	- Periodically snapshotted into the model

	This way, if for any reason we loose the REDIS reflection, the data
	can be synced back to the database using the model snapshot.
	"""

	#: The snapshot of the analytics data
	#: (Uncomment this when the reflection is actually implemented)
	#analyticsSnapshotData = models.TextField(null=True, default=None)
	#analyticsSnapshotTime = models.IntegerField(null=True, default=None)

	def analytics_key(self):
		"""
		Return the analytics key for the base model
		"""

		# Get FQN of the base class
		fqn = self.__module__ + "." + self.__class__.__name__

		# Get the name of the primary key field name
		pkf = self._meta.pk.name

		# Generate a unique for this entry analytics tracking ID
		return "analytics.%s.inst-%s" % (fqn, str(getattr(self, pkf)))

	def analytics(self):
		"""
		Return the analytics tracking class
		"""
		
		# Return an analytics class within the model's namespace
		return Analytics( self.analytics_key() )

