#!/bin/bash
################################################################
# CreditPiggy - A Community Credit Management System
# Copyright (C) 2013 Ioannis Charalampidis
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

# Deploy script for installing creditpiggy application
# into the apache2 configuration

# Locate apache directoriy
APACHE_DIR="/etc/httpd/conf.d"
[ ! -d ${APACHE_DIR} ] && echo "Could not locate Apache conf.d directory in ${APACHE_DIR}!" && exit 1

# Locate project directory
PROJECT_DIR="$(pwd)"
[ ! -d ${APACHE_DIR} ] && echo "Could not locate Apache conf.d directory in ${APACHE_DIR}!" && exit 1

cat <<EOF > ${APACHE_CONF}
WSGIScriptAlias / /home/creditpiggy/creditpiggy/creditpiggy/creditpiggy/wsgi.py
WSGIPythonPath /home/creditpiggy/creditpiggy/creditpiggy

<Directory /home/creditpiggy/creditpiggy/creditpiggy/creditpiggy>
	<Files wsgi.py>
	Require all granted
	</Files>
</Directory>
EOF