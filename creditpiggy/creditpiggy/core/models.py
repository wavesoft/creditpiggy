from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(models.Model):
	"""
	A real CreditPiggy user, that can have one or more 
	SocialUser or other profiles associated with it.
	"""
	pass

class AuthUser(AbstractUser):
	"""
	User credentials used for authentication with CreditPiggy.
	One or more authentication credentials can point to the same user.
	"""
	profile = models.ForeignKey(UserProfile, null=True)

