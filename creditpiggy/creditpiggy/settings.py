"""
Django settings for creditpiggy project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import creditpiggy.config as _CONFIG_
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9_$bpiycshlc8!otn771kf4+kumlvx0sc(ynqfyb@6(g2*^)*o'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [ "creditpiggy.cern.ch" ]

# - Social Auth ---

# Authentication user model
AUTH_USER_MODEL = 'core.AuthUser'

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
LOGIN_REDIRECT_URL = '/profile/'
LOGIN_ERROR_URL = '/login/'

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

    # - Social Auth ---
    'social.apps.django_app.default',
    # -----------------
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

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


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.7/howto/static-files/

STATIC_URL = '/static/'
