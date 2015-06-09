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
import importlib
import logging

from django.conf import settings
from threading import Thread

from creditpiggy.core.redis import share_redis_connection

# Get housekeeping logger
logger = logging.getLogger(__name__)

def periodical(seconds=None, minutes=None, hours=None, days=None, months=None, 
				priority=0, parallel=True, speedrun=True):
	"""
	Decorator that registers a housekeeping function to be executed periodically,
	with the interval specified.

	@param int 	priority - Higher priority tasks are executed earlier.
	@param bool parallel - A flag to denote that this task is time-critical and must run in parallel with others.
	@param bool speedrun - If True, and if for any reason the housekeeping process runs late, the function will be called as many times as required in order to catch-up.  
	"""
	def decorator(func):

		# Calculate interval
		interval = 0
		if seconds != None:
			interval += seconds
		if minutes != None:
			interval += minutes * 60
		if hours != None:
			interval += hours * 3600
		if days != None:
			interval += days * 86400

		# Register the function for post-processing by the class decorator
		func._periodical = True
		func._interval = interval
		func._priority = priority
		func._parallel = parallel
		func._speedrun = speedrun

		# Do not actually decorate the function
		return func
	return decorator

class HousekeepingTask:
	"""
	Base class where the housekeeping tasks derrive from
	"""
	
	# ==============================
	#  API Methods
	# ==============================

	def run(self, delta):
		"""
		Function executed when the housekeeping is running.
		The delta parameter contains the time since the last
		invocation of the housekeeping mechanism (in seconds)
		"""
		pass

	# ==============================
	#  Internal Methods
	# ==============================

	#: Functions with @periodical decorator
	_auto_periodicals = []

	def _locate_periodicals(self):
		"""
		Return an ordered list of automatically discovered methods with
		the @periodical decorator applied.
	
		This function inspects all the methods in the class and locates
		the ones decorated with the @periodical function. It then creates
		a description dictionary and bounds the method to the instance.
		"""

		# Lookup periodical functions
		periodicals = []
		for name, method in self.__class__.__dict__.iteritems():
			if hasattr(method, "_periodical"):

				# Store method in periodicals
				periodicals.append({
						"id": self.__class__.__module__ + "." + self.__class__.__name__ + "." + name,
						"method": method.__get__(self, self.__class__),
						"interval": method._interval,
						"priority": method._priority,
						"parallel": method._parallel,
						"speedrun": method._speedrun
					})

		# Sort periodicals by priority
		periodicals = sorted( periodicals, key=lambda k: k['priority'] )

		# Return description
		return periodicals


class HouseKeeping:
	"""
	The base HouseKeeping class that takes care of all the housekeeping
	operations in the CreditPiggy system.

	Register your HouseKeeping tasks in the CREDITPIGGY_HOUSEKEEPING_CLASSES
	tuple in the settings module.
	"""

	def __init__(self):
		"""
		Initialize the HouseKeeping class
		"""

		# Get a REDIS connection
		self.redis = share_redis_connection()

		# Initialize properties
		self.tasks = []
		self.lastRun = 0

		# Automated tasks (registered by decorators)
		self.auto = {
			'periodicals': []
		}

		# Iterate over registered api protocols
		for hk_cls in settings.CREDITPIGGY_HOUSEKEEPING_CLASSES:

			# Split module/class
			parts = hk_cls.split(".")
			p_module = ".".join(parts[0:-1])
			p_class = parts[-1]

			# Import module
			mod = importlib.import_module(p_module)

			# Get class reference
			cls = getattr(mod, p_class, None)
			if not cls:
				raise ImportError("Could not find class %s in module %s" % (p_class, p_module))

			# Instantiate housekeeping module
			inst = cls()
			self.tasks.append( inst )

			# Collect automated tasks
			self.auto['periodicals'] += inst._locate_periodicals()

	def run(self):
		"""
		Run the housekeeping tasks
		"""

		# Flag if run was clean or dirty
		clean = True

		# Get all the housekeeping timer indices
		last_times = self.redis.hgetall( "%shousekeeping/times" % settings.REDIS_KEYS_PREFIX )
		if not last_times:
			last_times = {}

		# Require some properties
		start_time = time.time()
		if not 'last' in last_times:
			last_times['last'] = start_time

		# Calculate the delta since last invocation & update last_times
		delta = start_time - float(last_times['last'])
		last_times['last'] = start_time

		# Run all the tasks in series
		# ----------------------------
		for t in self.tasks:
			try:
				t.run( delta )
			except Exception as f:
				logger.warn("Exception while running task %s.%s" % (t.__module__, t.__class__.__name__))
				logger.exception(f)

		# Collect all the tasks that needs to be performed
		# in parallel. Serial tasks are executed in-place
		parallel_tasks = []
		serial_tasks = []

		# Run automated tasks
		# -------------------
		#
		# 1) @periodical functions
		#
		for a_periodical in self.auto['periodicals']:
			try:
				# Check when it was invoked last
				last_time = 0
				if a_periodical['id'] in last_times:
					last_time = float(last_times[a_periodical['id']])

				# Check if enough time has passed for invocation
				delta = start_time - last_time
				if delta >= a_periodical['interval']:

					# If the method should run in parallel, create a thread
					# and store it on parallel_tasks. Otherwise, store it
					# in serial_tasks.
					if a_periodical['parallel']:
						parallel_tasks.append(Thread(target=a_periodical['method']))
					else:
						serial_tasks.append(a_periodical['method'])

					# Check if more than one intervals has passed
					if (delta >= a_periodical['interval'] * 2) and (last_time > 0) and (a_periodical['speedrun']):

						# Warn that we are going to do speed-run
						logger.warn("Task %s is late by %i iterations" % (a_periodical['id'], int(delta / a_periodical['interval'])))

						# Then don't update last_time to NOW, but just advance it one interval,
						# in order to call the processing logic once again on next run, which
						# is hopefully quick enough.
						last_times[a_periodical['id']] = a_periodical['interval'] + float(last_times[a_periodical['id']])

						# Mark the run as 'dirty', letting the caller know that it should
						# be called once again
						clean = False

					else:

						# Otherwise just update last_times of this function
						last_times[a_periodical['id']] = start_time

			except Exception as f:
				logger.warn("Exception while running periodical task %s" % a_periodical['id'])
				logger.exception(f)

		# Update last_times in redis
		self.redis.hmset( "%shousekeeping/times" % settings.REDIS_KEYS_PREFIX, last_times )

		# Start all parallel threads
		for t in parallel_tasks:
			t.start()

		# Run all serial tasks
		for t in serial_tasks:
			try:
				t()
			except Exception as f:
				logger.warn("Exception while running task %s.%s.%s" % (
					t.__self__.__module__, t.__self__.__class__.__name__, t.__name__))
				logger.exception(f)

		# Wait for all parallel tasks to complete
		for t in parallel_tasks:
			t.join()

		# Keep the last time we run this function
		self.lastRun = time.time()

		# Return TRUE if run was clean
		return clean

	def waitEvent(self, timeout=0):
		"""
		Wait until an event occures
		"""

		# (We currently support only @periodical tasks, and therefore
		#  we should wait for the minimum ammount of time required from 
		#  now till the moment one of the periodical tasks must be invoked)

		# Get all the housekeeping timer indices
		last_times = self.redis.hgetall( "%shousekeeping/times" % settings.REDIS_KEYS_PREFIX )
		if not last_times:
			last_times = {}

		# Get the maximum time to wait one way or another
		min_time = timeout
		if min_time <= 0:
			min_time = 60 # One minute if timeout is zero

		# Iterate over all housekeeping events, looking
		# for the minimum time to wait
		start_time = time.time()
		for a_periodical in self.auto['periodicals']:

			# Get last invokation time
			last_time = 0
			if a_periodical['id'] in last_times:
				last_time = float(last_times[a_periodical['id']])

			# Get delta
			delta = a_periodical['interval'] - (start_time - last_time)
			if delta < min_time:
				min_time = delta

			# If min_time is less than zero, we must exit now!
			if min_time < 0:
				logger.debug("A real-time event is pending")
				return

		# Wait min_time
		logger.info("Sleeping for %i seconds" % min_time)
		time.sleep(min_time)

