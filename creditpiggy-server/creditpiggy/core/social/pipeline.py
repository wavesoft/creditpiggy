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

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME

from social.pipeline.social_auth import social_user, AuthAlreadyAssociated
from social.apps.django_app.default.models import UserSocialAuth

from creditpiggy.api.auth import sso_update, website_from_request
from creditpiggy.api.models import WebsiteCredentials
from creditpiggy.core.email import send_welcome_email
from creditpiggy.core.models import merge_accounts

def social_update_displayname(backend, social, response={}, user=None, *args, **kwargs):
	"""
	Update user's display name
	"""

	# Locate icon
	profile_image = "/static/lib/img/anonymous.png"
	if social:
		if social.provider == "twitter":
			profile_image = response['profile_image_url']
		elif social.provider == "facebook":
			profile_image = 'http://graph.facebook.com/{0}/picture'.format(response['id'])
		elif social.provider == "google-oauth2":
			profile_image = response['image'].get('url')
		elif social.provider == "live":
			profile_image = 'https://apis.live.net/v5.0/{0}/picture'.format(response['id'])

	# If we don't have display name, create one
	dirty = False
	if not user.display_name:
		user.display_name = "%s %s" % (user.first_name, user.last_name)
		dirty = True

	# Update profile image
	if user.profile_image != profile_image:
		user.profile_image = profile_image
		dirty = True

	# Flush dirty
	if dirty:
		user.save()

def social_greet_user(user=None, is_new=False, *args, **kwargs):
	"""
	Greet new user
	"""

	# Welcome new users
	if is_new and not user is None:
		send_welcome_email( user )

def social_update_sso(strategy, backend, uid, response, user=None, *args, **kwargs):
	"""
	Update single-sign-on token for the specified user
	"""

	# If we have a user, try to get an SSO token
	if not user is None:

		# Lookup website from webid
		website = website_from_request( strategy.request, whitelistPath=True )
		if website:
			
			# Update user's SSO for this website
			sso_update( website, user, issue=True )

def social_user_withlink(backend, uid, response, user=None, *args, **kwargs):
	"""
	Simmilar function to 'social.pipeline.social_auth.social_user'
	but does not throw AuthAlreadyAssociated if the account that tries to be
	associated is already associated.
	"""

	try:
		# Call social user function as usual
		return social_user(backend=backend, uid=uid, user=user, response=response, *args, **kwargs)

	except AuthAlreadyAssociated:

		# When the user is already associated with another account
		# then IMPORT the OTHER account into the CURRENT account

		# Get some parameters from request
		provider = backend.name
		social = backend.strategy.storage.user.get_social_auth(provider, uid)
		print ">>> User in '%s' provider is '%r'" % (provider, social)
		print ">>> Current user '%r'" % (user,)

		# Merge the old_user to social.user
		merge_accounts( user, social.user )

		# Delete old user
		social.user.delete()

		# Switch social user to current user
		social.user = user
		social.save()

		# Return new social authentcation
		return {'social': social,
				'user': user,
				'is_new': False,
				'new_association': False}

