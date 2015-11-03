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

import copy

from collections import OrderedDict
from creditpiggy.core.models import to_dict, VisualMetric

class VisualMetrics(OrderedDict):
	"""
	Visual metrics information helper
	"""

	def __init__(self, visual_metrics):
		"""
		Initialize the metrics summarization helper, using the 
		specified iterable collection of VisualMetric objects as
		the base for the summarization.
		"""

		# Initialize dict
		super(VisualMetrics, self).__init__()

		# Keep local reference
		for vm in visual_metrics:
			# Get metric
			m  = to_dict( vm )

			# Init properties
			m['value'] = None

			# Store
			self[ vm.name ] = m

	def format(self, values=None):
		"""
		Format the specified values with the data included
		"""

		# If we don't have values, return my values
		if not values:
			return self

		# Iterate over the values
		ans = { }
		for k,v in values.iteritems():
			if k in self:

				# Copy metric description & Set value
				desc = copy.deepcopy( self[k] )
				desc['value'] = v
				desc['text'] = self.getDisplayValue( k, v )

				# Keep on anwer
				ans[k] = desc

		# Return answer
		return ans

	def getDisplayValue(self, metric, value):
		"""
		Calculate the display value of the spcified metric
		"""

		# If value is None, return as is
		if value is None:
			return ""

		# If that's an unknown value, return it as-is
		if not metric in self:
			return str(value)

		# Apply scale
		scaledValue = value * float(self[metric]['scale'])

		# Apply decimals
		return ("%%.%if" % self[metric]['decimals']) % scaledValue

class VisualMetricsSum(VisualMetrics):
	"""
	Visual metrics summarization helper
	"""

	def __init__(self, visual_metrics, timeseriesRate=None):
		"""
		Initialize the metrics summarization helper, using the 
		specified iterable collection of VisualMetric objects as
		the base for the summarization.
		"""

		# Initialize dict
		super(VisualMetricsSum, self).__init__(visual_metrics)

		# Initialize properties
		self.summarized = False
		self.timeseriesRate = timeseriesRate

		# Keep local reference
		for k in self.keys():

			# Init properties
			self[k]['value'] = None
			self[k]['samples'] = 0

	def merge(self, metrics):
		"""
		Merge the specified metrics object with our current state 
		"""

		# Iterate over local metrics
		for k,m in self.iteritems():

			# Check if we should average counters
			# or timeseries rates
			if not self.timeseriesRate:

				# Get counter value
				counter = metrics.counter(k, "")
				if not counter:
					counter = 0
				elif '.' in str(counter):
					counter = float(counter)
				else:
					counter = int(counter)

				# Apply summarization method
				if m['value'] is None:
					m['value'] = counter
				else:
					if (m['sum_method'] == VisualMetric.ADD) or (m['sum_method'] == VisualMetric.AVERAGE):
						m['value'] += counter
					elif m['sum_method'] == VisualMetric.MINIMUM:
						if counter < m['value']:
							m['value'] = counter
					elif m['sum_method'] == VisualMetric.MAXIMUM:
						if counter > m['value']:
							m['value'] = counter

			else:

				# Get counter rate
				rate = metrics.rates(self.timeseriesRate, k)

				# Rates are only summarised by average
				if m['value'] is None:
					m['value'] = rate[0]
				else:
					m['value'] += rate[0]

			# Increment samples
			m['samples'] += 1

		# We are not summarized
		self.summarized = False

	def finalize(self):
		"""
		Finalize summarization
		"""

		# Apply summarization when needed (if we are using rate we are only summarising)
		if not self.summarized and (self.timeseriesRate is None):

			# Iterate over metrics that need summarization
			for k, m in self.iteritems():
				if m['sum_method'] == VisualMetric.AVERAGE:
					m['value'] /= m['samples']

			# We are now summarized
			self.summarized = True

		# Calculate display value for every property
		for k, m in self.iteritems():
			m['text'] = self.getDisplayValue( k, m['value'] )

