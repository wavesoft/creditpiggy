
import hashlib
# from creditpiggy.frontend.models import ProjectRevision
# from creditpiggy.api.utils.jsonapi import APIError
# from creditpiggy.api.models import AuthToken, ProjectAuthToken

# def getRequestCredentials(request):
# 	"""
# 	Extract credentials from the request object
# 	"""

# 	# Initialize fields
# 	auth_user = None
# 	auth_secret = None

# 	# Look for 'api_key' and 'api_secret' in either GET or POST
# 	if 'api_key' in request.GET:
# 		if not 'api_secret' in request.GET:
# 			return None
# 		auth_user = request.GET['api_key']
# 		auth_secret = request.GET['api_secret']
# 	elif 'api_secret' in request.GET:
# 		return None

# 	elif 'api_key' in request.POST:
# 		if not 'api_secret' in request.POST:
# 			return None
# 		auth_user = request.POST['api_key']
# 		auth_secret = request.POST['api_secret']
# 	elif 'api_secret' in request.POST:
# 		return None

# 	# Return user/secret pair
# 	return (auth_user, auth_secret)

# def authenticateToken(key, secret):
# 	"""
# 	Validate key/secret combination and return the
# 	associated token object if it exists.
# 	"""

# 	# Lookup authentication token object
# 	try:

# 		# Get auth token
# 		authToken = AuthToken.objects.get(auth_key=key)

# 		# Validate checksum
# 		checksum = hashlib.sha512("%s:%s" % (authToken.auth_salt, secret)).hexdigest()
# 		if checksum != authToken.auth_hash:
# 			return None

# 		# Checksum validated
# 		return checksum

# 	except AuthToken.DoesNotExist:
# 		return None

# def authenticateProjectToken(token, project):
# 	"""
# 	Check if the specified token is valid for the given project
# 	"""

# 	# Lookup project
# 	project = None
# 	try:
# 		project = ProjectRevision.objects.get(uuid=project)
# 	except ProjectRevision.DoesNotExist:
# 		return None

# 	# Lookup token/project token
# 	token = None
# 	try:
# 		return ProjectAuthToken.objects.get(project=project, token=token)
# 	except ProjectAuthToken.DoesNotExist:
# 		return None

# def requireUserAuthToken():
# 	"""
# 	Decorator function to require a user authentication token
# 	"""
# 	def requireToken_decorator(func):
# 		def func_wrapper(*args, **kwargs):
			
# 			# Get first parameter (request)
# 			request = args[0]

# 			# Extract key/secret from request
# 			(key, secret) = getRequestCredentials(request)
# 			if not key:
# 				return APIError("Missing authentication credentials", 400)

# 			# Validate key/secret
# 			authToken = authenticateToken(key, secret)
# 			if not authToken:
# 				return APIError("You are not authorized to access this resource", 401)

# 			# Passthrough to the function
# 			return func(*args, **kwargs)

# 		return func_wrapper
# 	return requireToken_decorator


# def requireUserAuthToken(projectField=""):
# 	"""
# 	Decorator function to require a project authentication token
# 	"""
# 	def requireToken_decorator(func):
# 		def func_wrapper(*args, **kwargs):
			
# 			# Get first parameter (request)
# 			request = args[0]

# 			# Extract key/secret from request
# 			(key, secret) = getRequestCredentials(request)
# 			if not key:
# 				return APIError("Missing authentication credentials", 400)

# 			# Validate key/secret
# 			authToken = authenticateToken(key, secret)
# 			if not authToken:
# 				return APIError("You are not authorized to access this resource", 401)

# 			# Validate project authentication
# 			projectToken = authenticateProjectToken(authToken, kwargs[projectField])
# 			if not projectToken:
# 				return APIError("You are not authorized to access this project", 401)

# 			# Passthrough to the function
# 			return func(*args, **kwargs)

# 		return func_wrapper
# 	return requireToken_decorator
