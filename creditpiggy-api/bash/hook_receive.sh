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

# Get parameters from command-line
JOB_FILE=$1
JOB_ID=$2

[ -z "$JOB_FILE" ] && echo "ERROR: Missing job file (usage: $0 [job file] [uuid])" && exit 1
[ -z "$JOB_ID" ] && echo "ERROR: Missing job UUID (usage: $0 [job file] [uuid])" && exit 1

# Extract job ID
DIR=$(mktemp -d)
(

	# Extract job file
	cd $DIR
	tar -zxf ${JOB_FILE}

	# Parse job data
	VMID=""
	while read LINE; do
		KEY=$(echo "$LINE" | awk -F'=' '{print $1}')
		VAL=$(echo "$LINE" | awk -F'=' '{print $2}')

		# Update job counters
		if [ "$KEY" == "cpuusage" ]; then
			echo "counters,slot=${JOB_ID},job/cpuusage=${VAL}" | nc -U ${DAEMON_ENDPOINT}
		elif [ "$KEY" == "diskusage" ]; then
			echo "counters,slot=${JOB_ID},job/diskusage=${VAL}" | nc -U ${DAEMON_ENDPOINT}
		elif [ "$KEY" == "events" ]; then
			echo "counters,slot=${JOB_ID},job/events=${VAL}" | nc -U ${DAEMON_ENDPOINT}
		elif [ "$KEY" == "exitcode" ]; then
			if [ "${VAL}" == "0" ]; then
				echo "counters,slot=${JOB_ID},job/success=1" | nc -U ${DAEMON_ENDPOINT}
			else 
				echo "counters,slot=${JOB_ID},job/failure=1" | nc -U ${DAEMON_ENDPOINT}
			fi
		elif [ "$KEY" == "DUMBQ_VMID" ]; then
			VMID="${VAL}"
		fi

	done < jobdata

	# Claim or discard slot 
	if [ ! -z "$VMID" ]; then
		echo "claim,slot=${JOB_ID},machine=${VMID},credits=1" | nc -U ${DAEMON_ENDPOINT}
	else
		echo "discard,slot=${JOB_ID},reason=unknown-vmid" | nc -U ${DAEMON_ENDPOINT}
	fi

)

# Remove directory
rm -rf "${DIR}"

