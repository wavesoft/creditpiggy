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

from creditpiggy.frontend.views import account, projects, ajax, website, embed

urlpatterns = patterns('',
	url(r'^$', 								account.home, 				name="frontend.home"),
	url(r'^profile/$', 						account.profile, 			name="frontend.profile"),
	url(r'^logout/$',				 		account.logout, 			name="frontend.logout"),
	url(r'^login/$', 						account.login, 				name="frontend.login"),
	url(r'^login/done/$',	 				account.login_ack, 			name="frontend.login.done"),
	url(r'^login/pin/$',	 				account.login_pin, 			name="frontend.login.pin"),
	url(r'^status/$', 						account.status, 			name="frontend.status"),
	url(r'^test/$', 						account.test, 				name="frontend.test"),
	url(r'^credits/$', 						account.credits, 			name="frontend.credits"),
	url(r'^link/(?P<provider>[^/]+)/$',		account.link,				name="frontend.link"),

	url(r'^dashboard/overview/$',		 							account.dashboard_overview_overall,	 name="frontend.dashboard"),
	url(r'^dashboard/overview/project-(?P<project>[^/]+)$', 		account.dashboard_overview_project,	 name="frontend.dashboard.overview.project"),
	url(r'^dashboard/overview/campaign-(?P<campaign>[^/]+)$', 		account.dashboard_overview_campagin, name="frontend.dashboard.overview.campaign"),
	url(r'^dashboard/settings/$',		 	account.dashboard_settings,	name="frontend.dashboard.settings"),
	url(r'^dashboard/history/$',		 	account.dashboard_history,	name="frontend.dashboard.history"),

	url(r'^projects/$', 					projects.list,	 			name="frontend.projects"),
	url(r'^project/(?P<slug>[^/]+)/$', 		projects.details,	 		name="frontend.details"),

	url(r'^website/$', 						website.auto,	 			name="frontend.website"),
	url(r'^website/(?P<slug>[^/]+)/$', 		website.status,	 			name="frontend.website.status"),

	url(r'^ajax/profile\.(?P<cmd>[^/]+)/$',	ajax.profile,				name="frontend.ajax.profile"),
	url(r'^ajax/fetch\.(?P<cmd>[^/]+)/$',	ajax.fetch,					name="frontend.ajax.fetch"),
	url(r'^ajax/graph\.(?P<cmd>[^/]+)/$',	ajax.graph,					name="frontend.ajax.graph"),
	url(r'^ajax/login\.(?P<cmd>[^/]+)/$',	ajax.login,					name="frontend.ajax.login"),

	url(r'^embed/mystatus/$',	 			embed.mystatus,				name="frontend.embed.mystatus"),

)
