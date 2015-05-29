from django.conf.urls import patterns, include, url
from creditpiggy.api.views import project

urlpatterns = patterns('',
	
	url(r'^project/alloc\.(?P<api>[^/]+)$',		project.slot_alloc,			name="api.project.alloc" ),
	url(r'^project/claim\.(?P<api>[^/]+)$',		project.slot_claim,			name="api.project.claim" ),
	url(r'^project/meta\.(?P<api>[^/]+)$',		project.slot_meta,			name="api.project.meta" ),
	url(r'^project/counters\.(?P<api>[^/]+)$',	project.slot_counters,		name="api.project.counters" ),
	url(r'^project/bulk\.(?P<api>[^/]+)$',		project.bulk_commands,		name="api.project.bulk" ),

	# url(r'^(?P<project_id>[0-9a-f]+)/serve/(?P<token_id>[\w]+)$', views.project_serve),
	# url(r'^(?P<project_id>[0-9a-f]+)/report/(?P<token_id>[\w]+)$', views.project_report),
)
