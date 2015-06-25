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

DAEMON_ENDPOINT="/var/run/creditapi.socket"
COMMAND_LOG=""

# Get parameters from command-line
JOB_FILE=$1
JOB_ID=$2

[ -z "$JOB_FILE" ] && echo "ERROR: Missing job file (usage: $0 [job file] [uuid])" && exit 1
[ -z "$JOB_ID" ] && echo "ERROR: Missing job UUID (usage: $0 [job file] [uuid])" && exit 1

# Execute command
function doit {
	if [ -z "$COMMAND_LOG" ]; then
		cat | nc -U ${DAEMON_ENDPOINT}
	else
		cat | tee -a "${COMMAND_LOG}" | nc -U ${DAEMON_ENDPOINT}
	fi
}

# Forward command to daemon
echo "alloc,slot=${JOB_ID}" | doit
