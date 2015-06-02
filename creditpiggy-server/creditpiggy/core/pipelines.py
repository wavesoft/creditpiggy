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
from social.pipeline.social_auth import social_user
from social.apps.django_app.default.models import UserSocialAuth

def social_update_displayname(backend, user=None, *args, **kwargs):
	"""
	Update user's display name
	"""

	# If we don't have display name, create one
	if not user.display_name:
		user.display_name = "%s %s" % (user.first_name, user.last_name)
		user.save()

def social_user_withlink(backend, uid, request, user=None, *args, **kwargs):
	"""
	Simmilar function to 'social.pipeline.social_auth.social_user'
	but does not throw AuthAlreadyAssociated if the account that tries to be
	associated is already associated.
	"""

	# Check if we are trying to link a user
	login_mode = backend.strategy.session_get('mode')
	if login_mode != "link":
		# If not, just use the current function
		return social_user(backend, uid, user, *args, **kwargs)

	# Get provider and social user
	provider = backend.name
	social = backend.strategy.storage.user.get_social_auth(provider, uid)
	print ">>> User in '%s' provider is '%r'" % (provider, social)
	print ">>> Current user '%r'" % (user,)

	# Get all social profiles associated with my current account
	if social:

		# Handle the cases where the user tries to link a social
		# account with another profile already linked to another profile.

		if user and social.user != user:
			print ">>>>>>>>>>> CLASH DETECTED <<<<<<<<<<<<<<<"
			for account in user.social_auth.all():

				# Get the user account from the old social profile
				old_user = account.user

				# Switch account's profile to the one obtained
				# from the social account
				account.user = social.user
				account.save()

				# Fuse user accounts
				print ">>> Todo: Fuse(%r -> %r)" % (old_user, social.user)

				# Delete old user
				old_user.delete()

			# Use the user account from the social profile
			user = social.user

	return {'social': social,
			'user': user,
			'is_new': user is None,
			'new_association': False}
