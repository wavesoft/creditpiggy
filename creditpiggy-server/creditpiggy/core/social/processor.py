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

def social_login_redirect(request):
    """
    Load current redirect to context.
    """
    value = request.method == 'POST' and \
                request.POST.get(REDIRECT_FIELD_NAME) or \
                request.GET.get(REDIRECT_FIELD_NAME)
    querystring = value and (REDIRECT_FIELD_NAME + '=' + value) or ''

    ">>>>>>>> %r" % dir(request)

    return {
        'REDIRECT_FIELD_NAME': REDIRECT_FIELD_NAME,
        'REDIRECT_FIELD_VALUE': value,
        'REDIRECT_QUERYSTRING': querystring
    }
