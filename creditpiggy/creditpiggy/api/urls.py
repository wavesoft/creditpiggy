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

from django.conf.urls import patterns, include, url
from creditpiggy.api.views import project

urlpatterns = patterns('',
	
	# Default Protocol
	url(r'^project/alloc$',						project.slot_alloc,			name="api.project.alloc" ),
	url(r'^project/claim$',						project.slot_claim,			name="api.project.claim" ),
	url(r'^project/meta$',						project.slot_meta,			name="api.project.meta" ),
	url(r'^project/counters$',					project.slot_counters,		name="api.project.counters" ),
	url(r'^project/bulk$',						project.bulk_commands,		name="api.project.bulk" ),

	# Explicit protocol
	url(r'^project/alloc\.(?P<api>[^/]+)$',		project.slot_alloc,			name="api.project.alloc" ),
	url(r'^project/claim\.(?P<api>[^/]+)$',		project.slot_claim,			name="api.project.claim" ),
	url(r'^project/meta\.(?P<api>[^/]+)$',		project.slot_meta,			name="api.project.meta" ),
	url(r'^project/counters\.(?P<api>[^/]+)$',	project.slot_counters,		name="api.project.counters" ),
	url(r'^project/bulk\.(?P<api>[^/]+)$',		project.bulk_commands,		name="api.project.bulk" ),


	# url(r'^(?P<project_id>[0-9a-f]+)/serve/(?P<token_id>[\w]+)$', views.project_serve),
	# url(r'^(?P<project_id>[0-9a-f]+)/report/(?P<token_id>[\w]+)$', views.project_report),
)
