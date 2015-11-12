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
from django.template import Context
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives

def send_email( template, subject, to, raiseExceptions=False, **kwargs ):
	"""
	Send an arbitrary templated e-mail
	"""

	# Guard against exceptions
	try:

		# Skip if e-mail is not configured
		if not settings.EMAIL_HOST:
			return

		# Prepare context
		ctx_dict = {
			'base_url': settings.BASE_URL,
		}
		ctx_dict.update(kwargs)
		ctx = Context(ctx_dict)

		# Get payloads
		html = render_to_string("email/%s.html" % template, context=ctx)
		text = render_to_string("email/%s.txt" % template, context=ctx)

		# Send e-mail
		if isinstance(to, list):
			mail = EmailMultiAlternatives( body=text, subject=subject, to=[], bcc=to )
		else:
			mail = EmailMultiAlternatives( body=text, subject=subject, to=[to] )

		# Attach HTML version
		mail.attach_alternative(html, "text/html")
		mail.send()

	except Exception as e:

		# Re-throw exception if we should raise them
		if raiseExceptions:
			raise

def send_campaign_achievement_email( users, campaign_achievement, raiseExceptions=False ):
	"""
	Send an e-mail congratulating a group of people for their campaign achievement
	"""

	# Get e-mails of all users
	emails = []
	for u in users:
		if u.email_achievement:
			if u.email:
				emails.append( u.email )

	# If we have no e-mails, return
	if len(emails) == 0:
		return

	# Otherwise send it
	send_email(

		# Recepient
		"campaign_achievement", # Template
		"Achievement Unlocked: %s" % campaign_achievement.achievement.name, # Subject
		emails, # To
		raiseExceptions,

		# Context
		achievement=campaign_achievement.achievement,
		share_id=campaign_achievement.getShareID(),
		campaign=campaign_achievement.campaign,

		)

def send_personal_achievement_email( user, achievement, raiseExceptions=False ):
	"""
	Send an e-mail congratulating a user for his/her personal achievement
	"""

	# If user has opted-out from e-mails, do not send it
	if not user.email_achievement:
		return

	# Otherwise send it
	send_email(

		# Recepient
		"achievement", # Template
		"Achievement Unlocked: %s" % achievement.name, # Subject
		user.email, # To
		raiseExceptions,

		# Context
		achievement=achievement,
		share_id=achievement.getShareID(),
		project=None,
		user=user,

		)

def send_achievement_email( user, project, achievement, raiseExceptions=False ):
	"""
	Send an e-mail congratulating a user for his/her achievement
	"""

	# If user has opted-out from e-mails, do not send it
	if not user.email_achievement:
		return

	# Otherwise send it
	send_email(

		# Recepient
		"achievement", # Template
		"Achievement Unlocked: %s" % achievement.name, # Subject
		user.email, # To
		raiseExceptions,

		# Context
		achievement=achievement,
		share_id=achievement.getShareID(),
		project=project,
		user=user,

		)

def send_welcome_email( user, raiseExceptions=False ):
	"""
	Welcome user to a particular project
	"""
	send_email(

		# Recepient
		"welcome", # Template
		"Welcome to CreditPiggy", # Subject
		user.email, # To
		raiseExceptions,

		# Context
		user=user,

		)

def send_pin_email( pinLogin, raiseExceptions=False ):
	"""
	Send a PIN login e-mail to the specified user
	"""

	# Add spaces on pin
	pin = "%s-%s-%s" % (pinLogin.pin[0:2], pinLogin.pin[2:4], pinLogin.pin[4:6])

	# Send e-mail
	send_email(

		# Recepient
		"pinlogin", # Template
		"Login PIN: %s" % pin, # Subject
		pinLogin.user.email, # To
		raiseExceptions,

		# Context
		user=pinLogin.user,
		pin=pin,

		)

def send_custom_email( emails, subject, body, raiseExceptions=False ):
	"""
	Send a custom e-mail to specified targets
	"""

	# Send e-mail
	send_email(

		# Recepient
		"custom", # Template
		subject, # Subject
		emails, # To
		raiseExceptions,

		# Context
		body=body,
		title=subject,

		)
