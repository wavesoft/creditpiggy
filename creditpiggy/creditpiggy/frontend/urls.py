from django.conf.urls import patterns, include, url
from creditpiggy.frontend import views

urlpatterns = patterns('',
	url(r'^$', 				views.home, 		name="frontend.home"),
	url(r'^profile/$', 		views.profile, 		name="frontend.profile"),
	url(r'^logout/$', 		views.logout, 		name="frontend.logout"),
)
