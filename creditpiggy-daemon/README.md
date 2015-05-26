
# Creditpiggy Daemon

This folder contains the project-side daemon that is responsible for batching and throttling the requests to the creditpiggy server, minimizing the delays when interfacing with the application batch system.

## Configuration

In order to use the CreditPiggy daemon you will need to provide the following configuration:

```ApacheConf
# ===================================
# Creditpiggy API Configuration
# -----------------------------------
[api]

# Base URL for the creditpiggy server
url=http://test.local:8080/api

# Project authentication 
project_id=d6db27eb65704bb6acb3b83ceaf95e40
project_auth=561c18dedd604057b9f4852fda842faba5abbc09e7674bc5a4716d3d9d3a236f

# How frequently to flush the remote buffers (in seconds)
flush_interval=5

# ===================================
# Local daemon configuration
# -----------------------------------
[server]

# The pid file for the daemon
pidfile=/var/run/creditpiggy.pid

# Log level
# CRITICAL = 50
# ERROR    = 40
# WARNING  = 30
# INFO     = 20
# DEBUG    = 10
loglevel=20

# Log file
# Defaults to /dev/null, uncomment to enable logging
#logfile=/var/log/creditpiggy.log

# Uncomment the following to listen on a UNIX socket
#socket=unix
#bind=/var/run/creditapi

# Uncomment the following to listen on a UDP socket
socket=tcp
bind=0.0.0.0:9999
```

## Interfacing with the daemon

