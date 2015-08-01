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
		cat | nc -U ${DAEMON_ENDPOINT} >/dev/null
	else
		cat | tee -a "${COMMAND_LOG}" | nc -U ${DAEMON_ENDPOINT} >/dev/null
	fi
}

# Extract job ID
DIR=$(mktemp -d)
(

	# Extract job file
	cd $DIR
	tar -zxf ${JOB_FILE}
	VMID=""

	# If we have 'jobdata' process it
	if [ -f jobdata ]; then

		# Additional metadat
		COLLISION_TYPE="partons"
		EVENT_NUMBER=0
		ENERGY=1

		# Parse job data
		while read LINE; do
			KEY=$(echo "$LINE" | awk -F'=' '{print $1}')
			VAL=$(echo "$LINE" | awk -F'=' '{print $2}')

			# Update job counters
			if [ "$KEY" == "cpuusage" ]; then
				echo "counters,slot=${JOB_ID},job/cpuusage=${VAL}" | doit
			elif [ "$KEY" == "diskusage" ]; then
				echo "counters,slot=${JOB_ID},job/diskusage=${VAL}" | doit
			elif [ "$KEY" == "events" ]; then
				echo "counters,slot=${JOB_ID},job/events=${VAL}" | doit
				EVENT_NUMBER="${VAL}"
			elif [ "$KEY" == "exitcode" ]; then
				if [ "${VAL}" == "0" ]; then
					echo "counters,slot=${JOB_ID},job/success=1" | doit
				else 
					echo "counters,slot=${JOB_ID},job/failure=1" | doit
				fi
			elif [ "$KEY" == "runspec" ]; then
				# Get run specifications
				COLLISION_TYPE=$(echo "${VAL}" | awk '{ print $2 }')
				ENERGY=$(echo "${VAL}" | awk '{ print $4 }')
			elif [ "$KEY" == "DUMBQ_VMID" ]; then
				VMID="${VAL}"
			fi

		done < jobdata

		# Update your smashing counter
		echo "counters,slot=${JOB_ID},smashed/${COLLISION_TYPE}=${EVENT_NUMBER}" | doit

		# Update numbers
		ENERGY=$(echo ${ENERGY}*${EVENT_NUMBER} | bc)
		echo "counters,slot=${JOB_ID},collision/energy=${ENERGY}" | doit

	fi

	# Claim or discard slot 
	if [ ! -z "$VMID" ]; then
		echo "claim,slot=${JOB_ID},machine=${VMID},credits=1" | doit
	else
		echo "discard,slot=${JOB_ID},reason=unknown-vmid" | doit
	fi

)

# Remove directory
rm -rf "${DIR}"

