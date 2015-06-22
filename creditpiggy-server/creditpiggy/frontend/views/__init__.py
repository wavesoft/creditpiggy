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

def url_suffix(request):
	"""
	Calculate any required url suffix to be appended
	"""
	ans = ""

	# Forward 'webid'
	if hasattr(request, 'webid'):
		ans += "webid=%s" % request.webid
	elif 'webid' in request.GET:
		ans += "webid=%s" % request.GET['webid']

	# Return url suffix
	return ans

def context(request, **extra):
	"""
	Common context generator for all templates below
	"""
	
	# Check for webid
	webid = ""
	if hasattr(request, 'webid'):
		webid = request.webid

	# Return dict
	return dict({
		'url_suffix': url_suffix(request),
		'webid': webid
	}, **extra)

