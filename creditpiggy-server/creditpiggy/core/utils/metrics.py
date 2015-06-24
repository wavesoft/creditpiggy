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

from collections import OrderedDict
from creditpiggy.core.models import to_dict, VisualMetric

class VisualMetricsSum(OrderedDict):
	"""
	Visual metrics summarization helper
	"""

	def __init__(self, visual_metrics):
		"""
		Initialize the metrics summarization helper, using the 
		specified iterable collection of VisualMetric objects as
		the base for the summarization.
		"""

		# Initialize dict
		super(VisualMetricsSum, self).__init__()

		# Initialize properties
		self.summarized = False

		# Keep local reference
		for vm in visual_metrics:

			# Keep metric
			m  = to_dict( vm )

			# Init properties
			m['value'] = None
			m['samples'] = 0

			# Store
			self[ vm.name ] = m

	def merge(self, metrics):
		"""
		Merge the specified metrics object with our current state 
		"""

		# Iterate over local metrics
		for k,m in self.iteritems():

			# Get counter value
			counter = metrics.counter(k, "")
			if not counter:
				counter = 0
			elif '.' in str(counter):
				counter = float(counter)
			else:
				counter = int(counter)

			# Increment samples
			m['samples'] += 1

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

		# We are not summarized
		self.summarized = False

	def finalize(self):
		"""
		Finalize summarization
		"""

		# Apply summarization when needed
		if not self.summarized:

			# Iterate over metrics that need summarization
			for k, m in self.iteritems():
				if (m['sum_method'] == VisualMetric.AVERAGE):
					m['value'] /= m['samples']

			# We are now summarized
			self.summarized = True

