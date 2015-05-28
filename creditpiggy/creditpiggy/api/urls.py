from django.conf.urls import patterns, include, url
from creditpiggy.api import views

urlpatterns = patterns('',
	url(r'^(?P<project_id>[0-9a-f]+)/serve/(?P<token_id>[\w]+)$', views.project_serve),
	url(r'^(?P<project_id>[0-9a-f]+)/report/(?P<token_id>[\w]+)$', views.project_report),
)
