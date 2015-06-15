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

import random

from django.core.urlresolvers import reverse
from creditpiggy.api.models import SingleAuthLoginToken

def gen_crypto_key():
	"""
	Cryptographic key generator
	"""
	# Token charset
	charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_"
	key = ""
	for i in range(0, 48):
		key += charset[random.randint(0, len(charset)-1)]
	# Return a unique key
	return key

def compile_session(request):
	"""
	Compile session information
	"""

	# Get user
	user = request.user

	# Get/create session crypto-key
	if 'cryptokey' in request.session:
		ckey = request.session['cryptokey']
	else:
		ckey = gen_crypto_key()
		request.session['cryptokey'] = ckey

	# Common profile
	session = {
		
		# Cryptographic key for hashing and other session-wide operations
		"cryptokey": ckey,

		# Poll URLs
		"urls": {
			"login": reverse('frontend.login'),
			"logout": reverse('frontend.logout'),
			"profile": reverse('frontend.profile')
		}

	}

	# If user is authenticated, return profile
	if user.is_authenticated():

		# Lookup or create relevant single-auth token
		(token, created) = SingleAuthLoginToken.objects.get_or_create(user=user)

		# Insert user details
		session.update({
			"profile": user.profile(),
			"auth_token": token.token
		})
		return session

	# If not, return blank array
	else:
		return session

