from django.conf.urls import patterns, include, url
from django.contrib import admin

urlpatterns = patterns('',

	url('', 			include('creditpiggy.frontend.urls')),
	url(r'^api/', 		include('creditpiggy.api.urls')),

    # - Frameworks ----
	url(r'^admin/', 	include(admin.site.urls)),
    url('', include('social.apps.django_app.urls', namespace='social'))
    # -----------------

)
