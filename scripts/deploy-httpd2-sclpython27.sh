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

# Helper function to check if the specified package is installed
function isinstalled {
  if yum list installed "$@" >/dev/null 2>&1; then
    return 1
  else
    return 0
  fi
}

# Create a temporary file to use for logging
LOG_FILE=$(mktemp)

# Locate apache directoriy
APACHE_CONF_DIR="/etc/httpd/conf.d"
[ ! -d "${APACHE_CONF_DIR}" ] && echo "ERROR: Could not find conf.d in ${APACHE_CONF_DIR}!" && exit 1

# Locate project directory
PROJECT_DIR=$(pwd)
if [ -f "${PROJECT_DIR}/$(basename $0)" ]; then
	PROJECT_DIR=$(dirname $PROJECT_DIR)/creditpiggy-server
fi
[ ! -f "${PROJECT_DIR}/manage.py" ] && echo "ERROR: Could not find project dir in ${PROJECT_DIR}!" && exit 1

# Expect a directory where to deploy the server
DEPLOY_DIR=$1
[ -z "${DEPLOY_DIR}" ] && echo "ERROR: Please specify a directory where to deploy the server!" && exit 1
echo "Deploying project:"

# ===================================
# 1) Check environment
# ===================================

# Check python version
echo -n " - Checking python version..."
PYTHON_VER=$(python --version 2>&1 | awk '{print $2}')
HAS_PYTHON_27=$(echo $PYTHON_VER | grep -c '2.7')
USE_SCL=0
if [ ${HAS_PYTHON_27} -eq 0 ]; then
	echo "${PYTHON_VER} (will use scl)"
	USE_SCL=1
else
	echo "${PYTHON_VER} (asuming default configuration)"
fi

# If we need SCL check the status
if [ $USE_SCL -eq 1 ]; then

	echo -n " - Checking for Python2.7 DSC repo..."
	grep -c "http://people.redhat.com/bkabrda/python27-rhel-6" /etc/yum.repos.d/* -Rq
	if [ $? -ne 0 ]; then

		# Install the Python 2.7 Dynamic Software Collection repos
		wget -qO- http://people.redhat.com/bkabrda/scl_python27.repo >> /etc/yum.repos.d/scl_python27.repo 2>LOG_FILE
		if [ $? -ne 0 ]; then
			echo "error"
			cat $LOG_FILE
			rm $LOG_FILE
			exit 1
		fi

		# Check if that worked out
		if [ $(yum search python27 -q 2>&1 | grep -c "No matches found") -eq 0 ]; then
			echo "failed"
			echo "ERROR: Could not locate python27 package after installing the Python27 Dynamic Software Collection!"
			exit 1
		fi
		echo "ok"

		# Check if it's not installed
		echo -n " - Checking for python27 installation..."
		if [ $(scl -l 2>&1 | grep -c python27) -eq 0 ]; then
			# Install now
			yum -y install python27 >$LOG_FILE 2>$LOG_FILE
			if [ $? -ne 0 ]; then
				echo "error"
				cat $LOG_FILE
				rm $LOG_FILE
				exit 1
			fi
			echo "installed"
		else
			echo "ok"
		fi

	else
		echo "exists"
	fi

	# Export library directories for further use in this script
	export LD_LIBRARY_PATH="$LD_LIBRARY_PATH:/opt/rh/python27/root/lib:/opt/rh/python27/root/lib64:/opt/rh/python27/root/usr/lib:/opt/rh/python27/root/usr/lib64"

	# Define the PIP utility to use for further processing
	PYTHON_PIP="/opt/rh/python27/root/usr/bin/pip"

	# Check if we have PIP in SCI environment
	echo -n " - Checking for 'pip' in python27..."
	if [ ! -f "${PYTHON_PIP}" ]; then

		# Use easy_install to install pip
		/opt/rh/python27/root/usr/bin/easy_install-2.7 pip >$LOG_FILE 2>$LOG_FILE
		if [ $? -ne 0 ]; then
			echo "error"
			cat $LOG_FILE
			rm $LOG_FILE
			exit 1
		fi
		echo "installed"

	else
		echo "ok"
	fi

	# Locate python MOD_WSGI from SCP repo
	APACHE_MODWSGI_SCL="/opt/rh/python27/root/usr/lib64/python2.7/site-packages/mod_wsgi/server/mod_wsgi-py27.so"

	# Check if we have mod_wsgi
	echo -n " - Checking for 'mod_wsgi' in python27..."
	if [ ! -f ${APACHE_MODWSGI_SCL} ]; then
		echo "missing"

		# We will need gcc for building mod_wsgi
		echo -n " - Checking for 'gcc'..."
		if isinstalled "gcc"; then
			echo "ok"
		else
			# Install now
			yum -y install gcc >$LOG_FILE 2>$LOG_FILE
			if [ $? -ne 0 ]; then
				echo "error"
				cat $LOG_FILE
				rm $LOG_FILE
				exit 1
			fi
			echo "installed"
		fi

		# We will need httpd-devel for building mod_wsgi
		echo -n " - Checking for 'httpd-devel'..."
		if isinstalled "httpd-devel"; then
			echo "ok"
		else
			# Install now
			yum -y install httpd-devel >$LOG_FILE 2>$LOG_FILE
			if [ $? -ne 0 ]; then
				echo "error"
				cat $LOG_FILE
				rm $LOG_FILE
				exit 1
			fi
			echo "installed"
		fi

		# Use pip to install mod_wsgi
		${PYTHON_PIP} install mod_wsgi >$LOG_FILE 2>$LOG_FILE
		if [ $? -ne 0 ]; then
			echo "error"
			cat $LOG_FILE
			rm $LOG_FILE
			exit 1
		fi

		# If the file is still missing something went wrong
		if [ ! -f ${APACHE_MODWSGI_SCL} ]; then
			echo "error"
			echo "ERROR: Unable to locate ${APACHE_MODWSGI_SCL}"
		fi

		# We have it now
		echo "installed"
	else
		echo "ok"
	fi

else

	# Install missing mod_wsgi package
	echo -n " - Checking for 'mod_wsgi'..."
	if isinstalled "mod_wsgi"; then
		echo "ok"
	else
		# Install now
		yum -y install mod_wsgi >$LOG_FILE 2>$LOG_FILE
		if [ $? -ne 0 ]; then
			echo "error"
			cat $LOG_FILE
			rm $LOG_FILE
			exit 1
		fi
		echo "installed"
	fi

	# Install missing python-pip package
	echo -n " - Checking for 'python-pip'..."
	if isinstalled "python-pip"; then
		echo "ok"
	else
		# Install now
		yum -y install python-pip >$LOG_FILE 2>$LOG_FILE
		if [ $? -ne 0 ]; then
			echo "error"
			cat $LOG_FILE
			rm $LOG_FILE
			exit 1
		fi
		echo "installed"
	fi

	# Use system pip utility
	PYTHON_PIP=$(which pip 2>&1)
	if [ -z "$PYTHON_PIP" ]; then
		echo "ERROR: Could not locate installed pip binary!"
		exit 1
	fi

fi

# Install DJANGO if missing
DJANGO_VER=$(${PYTHON_PIP} list | grep Django | awk '{print $2}' | tr -d '()')
echo -n " - Checking for Django..."
if [ -z "$DJANGO_VER" ]; then

	# Use pip to install django
	${PYTHON_PIP} install django >$LOG_FILE 2>$LOG_FILE
	if [ $? -ne 0 ]; then
		echo "error"
		cat $LOG_FILE
		rm $LOG_FILE
		exit 1
	fi
	echo "installed"
	
else
	echo "ok ($DJANGO_VER)"
fi

# ===================================
# 1) Setup directories
# ===================================

# Create directory structure
echo -n " - Creating directory structure..."
mkdir -p ${DEPLOY_DIR}/htdocs
mkdir -p ${DEPLOY_DIR}/logs
mkdir -p ${DEPLOY_DIR}/conf
mkdir -p ${DEPLOY_DIR}/virtualenv
echo "ok"

# Create a virtualenv on the 

# Prepare creditpiggy HTTPD configuration and store it on config
echo -n "Adding creditpiggy.conf..."
if [ ! -f "${DEPLOY_DIR}/conf/httpd-creditpiggy.conf" ]; then

	# Create config file
	cat <<EOF > ${DEPLOY_DIR}/conf/httpd-creditpiggy.conf
WSGIScriptAlias / ${PROJECT_DIR}/creditpiggy/wsgi.py
WSGIPythonPath ${PROJECT_DIR}

<Directory ${PROJECT_DIR}/creditpiggy>
	<Files wsgi.py>
	Require all granted
	</Files>
</Directory>
EOF
	echo "ok"

else
	echo "exists"
fi

# Update SELinuxPolicy
echo "Updating SELinux policies..."
if [ ! -z "$(which semanage)" ]; then

	# Add read-only httpd content in the project directory
	semanage fcontext -a -t httpd_sys_content_t "${PROJECT_DIR}(/.*)?"

	# Update policy
	restorecon -Rv ${PROJECT_DIR}

fi
