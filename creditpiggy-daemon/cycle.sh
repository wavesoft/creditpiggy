#!/bin/bash

UUID=$(uuidgen)
MACHINE="b05eb435-e5e2-45ee-8efe-8018019a7a79"
MACHINE="test4"

echo "alloc,slot=${UUID}" | nc -U creditapi.socket
echo "counters,slot=${UUID},job/completed=1" | nc -U creditapi.socket
echo "claim,slot=${UUID},machine=${MACHINE},credits=1" | nc -U creditapi.socket
