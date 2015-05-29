
from django.conf import settings
from social.pipeline.social_auth import social_user
from social.apps.django_app.default.models import UserSocialAuth

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
