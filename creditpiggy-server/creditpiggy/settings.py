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

"""
Django settings for creditpiggy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

import sys

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Try to import config
try:
	import etc.settings as _CONFIG_
except ImportError as e:
	raise Exception("Apply your settings to config.py using config.py.example as reference!")

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9_$bpiycshlc8!otn771kf4+kumlvx0sc(ynqfyb@6(g2*^)*o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
TEMPLATE_DEBUG = True
ALLOWED_HOSTS = [ ]

# If we have debug attributes defined, apply from config
if hasattr(_CONFIG_, 'DEBUG'):
	DEBUG = _CONFIG_.DEBUG
	ALLOWED_HOSTS = _CONFIG_.ALLOWED_HOSTS

# Logging
LOGGING =  _CONFIG_.LOGGING

# Caches
CACHES = {
	'default': {
		"BACKEND": "django_redis.cache.RedisCache",
		"LOCATION": "redis://%s:%i/%i" % (_CONFIG_.REDIS_HOST, _CONFIG_.REDIS_PORT, _CONFIG_.REDIS_DB),
		"OPTIONS": {
			"CLIENT_CLASS": "django_redis.client.DefaultClient",
		}
	},
}

# Session engine: Use Cache
SESSION_ENGINE = "django.contrib.sessions.backends.cache"

# API Session
SESSION_COOKIE_NAME_API = "sessionfor"
WEBID_COOKIE_NAME = "_cpwebid"
WEBID_COOKIE_SALT = "xbo37ga86v31"

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases
DATABASES = {
	'default': _CONFIG_.DEFAULT_DATABASE
}

# REDIS Database Configuration
REDIS_HOST = _CONFIG_.REDIS_HOST
REDIS_PORT = _CONFIG_.REDIS_PORT
REDIS_DB = _CONFIG_.REDIS_DB
REDIS_KEYS_PREFIX = _CONFIG_.REDIS_KEYS_PREFIX

# Creditpiggy timeseries ring size
TS_VALUE_COUNT = _CONFIG_.TS_VALUE_COUNT

# Base URL
BASE_URL = _CONFIG_.BASE_URL

# How long to keep a credit slot alive before expiring it (in seconds)
# Defaults to 15 days
CREDITPIGGY_CREDIT_EXPIRE_TIME = 1296000

# Creditpiggy anonymous user
CREDITPIGGY_ANONYMOUS_PROFILE = _CONFIG_.CREDITPIGGY_ANONYMOUS_PROFILE

# CreditPiggy API Protocols
CREDITPIGGY_API_PROTOCOLS = (
	'creditpiggy.api.protocols.json.JSONProtocol',
	'creditpiggy.api.protocols.jsonp.JSONPProtocol',
	'creditpiggy.api.protocols.text.TEXTProtocol',
)

# Housekeeping clases 
CREDITPIGGY_HOUSEKEEPING_CLASSES = (
	'creditpiggy.core.metrics.MetricFeaturesHousekeeping',
	'creditpiggy.core.models.ModelHousekeeping',
)

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Static root
STATIC_ROOT = os.path.join(BASE_DIR, "creditpiggy/static")
STATICFILES_DIRS = (
	os.path.join(BASE_DIR, "static"),
)

# TinyMCE Configuration
TINYMCE_JS_URL = STATIC_URL + "lib/js/tinymce/tinymce.min.js"
TINYMCE_DEFAULT_CONFIG = {
	'plugins': "table,spellchecker,paste,searchreplace",
	'theme': "modern",
	'custom_undo_redo_levels': 10,
}

# - Social Auth ---

# Authentication user model
AUTH_USER_MODEL = 'core.PiggyUser'

# Google Social Authentication Details
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = _CONFIG_.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = _CONFIG_.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET

# Twitter Social Authentication Details
SOCIAL_AUTH_TWITTER_KEY = _CONFIG_.SOCIAL_AUTH_TWITTER_KEY
SOCIAL_AUTH_TWITTER_SECRET = _CONFIG_.SOCIAL_AUTH_TWITTER_SECRET

# Facebook Social Authentication Details
SOCIAL_AUTH_FACEBOOK_KEY = _CONFIG_.SOCIAL_AUTH_FACEBOOK_KEY
SOCIAL_AUTH_FACEBOOK_SECRET = _CONFIG_.SOCIAL_AUTH_FACEBOOK_SECRET
SOCIAL_AUTH_FACEBOOK_SCOPE = ['email']
SOCIAL_AUTH_FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'en_US'}

# MSN Live Authentication
SOCIAL_AUTH_LIVE_KEY = _CONFIG_.SOCIAL_AUTH_LIVE_KEY
SOCIAL_AUTH_LIVE_SECRET = _CONFIG_.SOCIAL_AUTH_LIVE_SECRET

# Social login redirection URLs
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/login/done/'
LOGIN_ERROR_URL = '/login/'

# Customize authentication pipeline to enable account linking
SOCIAL_AUTH_PIPELINE = (
	'social.pipeline.social_auth.social_details',
	'social.pipeline.social_auth.social_uid',
	'social.pipeline.social_auth.auth_allowed',

	# Overrides 'social.pipeline.social_auth.social_user'
	# in order to provide linking with p#reviously created profiles.
	#'creditpiggy.core.social.pipeline.sial_user_withlink',
	'social.pipeline.social_auth.social_user',

	'social.pipeline.user.get_username',
	'social.pipeline.user.create_user',
	'social.pipeline.social_auth.associate_user',
	'social.pipeline.social_auth.load_extra_data',
	'social.pipeline.user.user_details',

	'creditpiggy.core.social.pipeline.social_update_displayname',
	'creditpiggy.core.social.pipeline.social_update_sso',
	'creditpiggy.core.social.pipeline.social_greet_user',

)


# Storing additional fields in session, used for
# identifying linking requests
FIELDS_STORED_IN_SESSION = [ 'mode', 'a' ]

# -----------------

# Application definition

INSTALLED_APPS = (
	'django.contrib.admin',
	'django.contrib.auth',
	'django.contrib.contenttypes',
	'django.contrib.sessions',
	'django.contrib.messages',
	'django.contrib.staticfiles',
	'creditpiggy.core',
	'creditpiggy.api',
	'creditpiggy.frontend',
	'tinymce',

	# - Social Auth ---
	'social.apps.django_app.default',
	# -----------------
)

MIDDLEWARE_CLASSES = (
	#'django.contrib.sessions.middleware.SessionMiddleware',
	'creditpiggy.core.middleware.SessionWithAPIMiddleware',
	
	'django.middleware.common.CommonMiddleware',
	'django.middleware.csrf.CsrfViewMiddleware',
	'django.contrib.auth.middleware.AuthenticationMiddleware',
	'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
	'django.contrib.messages.middleware.MessageMiddleware',
	'django.middleware.clickjacking.XFrameOptionsMiddleware',
	
	'creditpiggy.core.middleware.TimezoneMiddleware',
	'creditpiggy.core.middleware.URLSuffixMiddleware',

	# - Social Auth ---
	'social.apps.django_app.middleware.SocialAuthExceptionMiddleware'
	# -----------------

)

AUTHENTICATION_BACKENDS = (

	# - Social Auth ---
	'social.backends.google.GoogleOAuth2',
	'social.backends.facebook.FacebookOAuth2',
	'social.backends.twitter.TwitterOAuth',
	'social.backends.live.LiveOAuth2',
	# -----------------

	'django.contrib.auth.backends.ModelBackend',
)


TEMPLATE_CONTEXT_PROCESSORS = (
	'django.contrib.auth.context_processors.auth',
	'django.core.context_processors.debug',
	'django.core.context_processors.i18n',
	'django.core.context_processors.media',
	'django.contrib.messages.context_processors.messages',
	# - Social Auth ---
	'social.apps.django_app.context_processors.backends',
	'social.apps.django_app.context_processors.login_redirect',
	# -----------------
)


ROOT_URLCONF = 'creditpiggy.urls'
WSGI_APPLICATION = 'creditpiggy.wsgi.application'

# Email configuration
DEFAULT_FROM_EMAIL = _CONFIG_.SMTP['FROM']
EMAIL_HOST = _CONFIG_.SMTP['HOST']
EMAIL_PORT = _CONFIG_.SMTP['PORT']
EMAIL_HOST_USER = _CONFIG_.SMTP['USER']
EMAIL_HOST_PASSWORD = _CONFIG_.SMTP['PASSWORD']
EMAIL_USE_TLS = _CONFIG_.SMTP['TLS']
EMAIL_USE_SSL = _CONFIG_.SMTP['SSL']

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Athens'

USE_I18N = True
USE_L10N = True
USE_TZ = True

