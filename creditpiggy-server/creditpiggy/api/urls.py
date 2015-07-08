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
from creditpiggy.api.views import batch
from creditpiggy.api.views import lib

urlpatterns = patterns('',
	
	# Default Protocol
	url(r'^batch/alloc$',						batch.slot_alloc,			name="api.batch.alloc" ),
	url(r'^batch/claim$',						batch.slot_claim,			name="api.batch.claim" ),
	url(r'^batch/discard$',						batch.slot_discard,			name="api.batch.discard" ),
	url(r'^batch/meta$',						batch.slot_meta,			name="api.batch.meta" ),
	url(r'^batch/counters$',					batch.slot_counters,		name="api.batch.counters" ),
	url(r'^batch/slots$',						batch.enum_slots,			name="api.batch.slots" ),
	url(r'^batch/bulk$',						batch.bulk_commands,		name="api.batch.bulk" ),

	url(r'^lib/session$',						lib.session,				name="api.lib.session" ),
	url(r'^lib/claim$',							lib.claim,					name="api.lib.claim" ),
	url(r'^lib/release$',						lib.release,				name="api.lib.release" ),
	url(r'^lib/thaw$',							lib.thaw,					name="api.lib.thaw" ),
	url(r'^lib/referrer$',						lib.referrer,				name="api.lib.referrer" ),

	# Explicit protocol
	url(r'^batch/alloc\.(?P<api>[^/]+)$',		batch.slot_alloc,			name="api.batch.alloc" ),
	url(r'^batch/claim\.(?P<api>[^/]+)$',		batch.slot_claim,			name="api.batch.claim" ),
	url(r'^batch/discard\.(?P<api>[^/]+)$',		batch.slot_discard,			name="api.batch.discard" ),
	url(r'^batch/meta\.(?P<api>[^/]+)$',		batch.slot_meta,			name="api.batch.meta" ),
	url(r'^batch/counters\.(?P<api>[^/]+)$',	batch.slot_counters,		name="api.batch.counters" ),
	url(r'^batch/slots\.(?P<api>[^/]+)$',		batch.enum_slots,			name="api.batch.slots" ),
	url(r'^batch/bulk\.(?P<api>[^/]+)$',		batch.bulk_commands,		name="api.batch.bulk" ),

	url(r'^lib/session\.(?P<api>[^/]+)$',		lib.session,				name="api.lib.session" ),
	url(r'^lib/claim\.(?P<api>[^/]+)$',			lib.claim,					name="api.lib.claim" ),
	url(r'^lib/release\.(?P<api>[^/]+)$',		lib.release,				name="api.lib.release" ),
	url(r'^lib/thaw\.(?P<api>[^/]+)$',			lib.thaw,					name="api.lib.thaw" ),
	url(r'^lib/referrer\.(?P<api>[^/]+)$',		lib.referrer,				name="api.lib.referrer" ),

)
