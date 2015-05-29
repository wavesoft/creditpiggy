
from django.conf import settings
import redis

#: The shared REDIS connection pool
shared_pool = None

def share_redis_connection():
	"""
	Get a shared REDIS connection by using a central redis pool
	"""

	# Initialize the shared_pool if not yet initialized
	global shared_pool
	if not shared_pool:
		shared_pool = redis.ConnectionPool( host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB )

	# Return a redis pool instance
	return redis.StrictRedis(connection_pool=shared_pool)

