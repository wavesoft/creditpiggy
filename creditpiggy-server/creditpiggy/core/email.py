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
		mail = EmailMultiAlternatives( body=text, subject=subject, to=to )
		mail.attach_alternative(html, "text/html")
		mail.send()

	except Exception as e:

		# Re-throw exception if we should raise them
		if raiseExceptions:
			raise

def send_achievement_email( user, project, achievement, raiseExceptions=False ):
	"""
	Send an e-mail congratulating a user for his/her achievement
	"""
	send_email(

		# Recepient
		"achievement", # Template
		"Achievement Unlocked: %s" % achievement.name, # Subject
		(user.email,), # To
		raiseExceptions,

		# Context
		achievement=achievement,
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
		(user.email,), # To
		raiseExceptions,

		# Context
		user=user,

		)

