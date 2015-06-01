
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

# Google OAuth2 Credentials
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = '158390263130-oi0kbg8qbdgrjlpl753jg9eod1oni5lq.apps.googleusercontent.com'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'Ln9dfgN_PjK2Kmb-3uzNmTwf'

# Twitter OAuth Credentials
SOCIAL_AUTH_TWITTER_KEY = '8vKVjCs3WDbcK2CBhPWLdxhYI'
SOCIAL_AUTH_TWITTER_SECRET = 'WFDO7P98apO7ggZfQO2mHgtTxvyWZreXofHY61RcJ2oya6LkMl'

# FAcebook OAuth2 Credentials
SOCIAL_AUTH_FACEBOOK_KEY = '409578749230025'
SOCIAL_AUTH_FACEBOOK_SECRET = 'ebdfea2636f4e38ba8c6e47f33233422'

# MSN Live OAuth2 Credentials
SOCIAL_AUTH_LIVE_KEY = "000000004414F6B7"
SOCIAL_AUTH_LIVE_SECRET = "ZXF5gRekFd61F--cgiNHntIqejfRKMzL"

# REDIS Database Configuration
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_KEYS_PREFIX = ""

# Default Database
DEFAULT_DATABASE = {
	'ENGINE': 'django.db.backends.sqlite3',
	'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
}