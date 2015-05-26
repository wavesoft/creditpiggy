#!/usr/bin/env python
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

import sys
import os
import json
import atexit
import time
import logging
import requests
import threading
import signal
import SocketServer
import Queue
import ConfigParser

class CPRemoteAPIServer(threading.Thread):
	"""
	Server class that batches, throttles and forwards the requests
	to the remote CreditPiggy server.
	"""

	def __init__(self, config):
		"""
		Initialize remote API
		"""

		# Prepare properties
		self.config = config
		self.shutdownFlag = False
		self.ingress_queue = Queue.Queue()

		# Create logger
		self.logger = logging.getLogger("remote")

	def handshake(self):
		"""
		Perform a handshake to ensure everything works as expected
		"""
		return True

	def send(self, command, arguments={}):
		"""
		Send a command to CreditPiggy
		"""

		pass

	def run(self):
		"""
		Main thread
		"""

		# Create local variables
		stacks = {}
		flush_time = 0
		cmd_counter = 0

		# Remote API infinite loop
		while not self.shutdownFlag:

			# Wait for a message on the ingress queue
			try:

				# Wait for message
				msg = self.ingress_queue.get(True, 0.1)

				# Process
				msg = json.loads(msg)

				# Make sure the appropriate stack exists
				if not msg["cmd"] in stacks:
					stacks[msg["cmd"]] = []

				# Put message the appropriate stack
				stacks[msg["cmd"]].append(msg["args"])
				cmd_counter += 1

				# Flush in 5 seconds
				flush_time = time.time() + self.config['flush_interval']

				# Debug
				self.logger.debug("Stacking command '%s'" % msg["cmd"])

			except Queue.Empty:
				# If queue is empty, just continue the loop,
				# checking for a shutdown flag
				pass

			# Flush stacks periodically
			if (flush_time > 0) and (time.time() > flush_time) and stacks:

				# Send a batch command
				self.logger.info("Flushing %i commands on stack" % cmd_counter)
				self.send("batch", stacks)

				# Reset variables
				stacks = {}
				flush_time = 0
				cmd_counter = 0

		# Send stacks if pending
		if stacks:
			self.logger.warn("Flushing %i commands on stack" % cmd_counter)
			self.send("batch", stacks)

	def shutdown(self):
		"""
		Shutdown server by interrupting the loop
		"""
		self.shutdownFlag = True

class CPLocalRequestHandler(SocketServer.BaseRequestHandler):
	"""
	Request handler for the requests that come from the 
	local API endpoint.
	"""

	def handle(self):
		"""
		Handle an API request
		"""

		# Create logger
		logger = logging.getLogger("local")

		# Fetch command
		data = self.request.recv(1500).strip()

		# Split into [command,[arg=vale,...]]
		parts = data.split(",", 1)
		c_command = str(parts[0]).upper()
		c_args = ""
		k_args = {}

		# Tokenize arguments
		if len(parts) > 1:
			parts = parts[1].split(",")
			for p in parts:
				kv = p.split("=")
				k_args[kv[0]] = kv[1]

		# Log message
		logger.debug("Handing command '%s'" % c_command)

		# Handle commands
		if c_command == "ALLOC":
			# --------------------------------------------------
			#
			# Syntax: ALLOC,job=<uuid>,[min=n,max=n|credits=n]
			#
			#   Desc: Denote that the specified UUID is a valid
			#         job ID assigned to this project.
			#
			# Params:   job= : The project's job unique ID
			#			min= : The minimum accepted value of 
			#                  credits to accept for this job.
			#           max= : The maximum accepted value of
			#                  credits to accept for this job.
			#       credits= : The excact value of credits to
			#                  give upon completing the job.
			#
			# --------------------------------------------------

			# Forward the request to the remote server
			self.server.queue_message("alloc", k_args )

			# Send 'OK'
			self.request.sendall("OK")

		elif c_command == "CLAIM":
			# --------------------------------------------------
			#
			# Syntax: CLAIM,job=<uuid>,machine=<machine_id>,[credit=n]
			#
			#   Desc: Mark the specified job as 'claimed' by the
			#         specified machine ID. Optionally, specify
			#         the credits granted to this machine from
			#         the results of the job. If not specified,
			#         it's expected to match the credits allocated
			#         to the job in the 'ALLOC' phase.
			#
			# --------------------------------------------------

			# Forward the request to the remote server
			self.server.queue_message("claim", k_args )

			# Send 'OK'
			self.request.sendall("OK")

		elif c_command == "COUNTERS":
			# --------------------------------------------------
			#
			# Syntax: COUNTERS,job=<uuid>,[name=n]
			#
			#   Desc: Define or update counters for the specified
			#         job. Such counters might be errors, events,
			#         or other metrics useful in calculating goals.
			#
			#         Such counters are aggregated to the user's
			#         profile.
			#
			# --------------------------------------------------

			# Forward the request to the remote server
			self.server.queue_message("counters", k_args )

			# Send 'OK'
			self.request.sendall("OK")

		else:

			# Unknown command, send 'ER' to indicate that
			# an error occured.
			self.request.sendall("ER")

class CPThreadedLocalAPIServer(SocketServer.ThreadingMixIn):
	"""
	Threaded local API server base logic, this is flavored
	for UDP, TCP or UNIX Sockets later.
	"""

	def __init__(self, ingress_queue):
		"""
		Initialize the threaded local API server
		"""

		# Keep a reference of the ingress queue
		self.ingress_queue = ingress_queue

		# Create logger
		self.logger = logging.getLogger("remote-server")

	def queue_message(self, command, args={}):
		"""
		Enqueue a message on the ingress queue
		"""

		self.logger.debug("Queueing command '%s'" % command)

		# Forward to ingress queue
		self.ingress_queue.put(json.dumps({
				"cmd": command,
				"args": args
			}))

class CPUNIXServer(CPThreadedLocalAPIServer, SocketServer.UnixStreamServer):
	def __init__(self, server_address, RequestHandlerClass, ingress_queue):
		# Initialize superclasses
		SocketServer.UnixStreamServer.__init__(self, server_address, RequestHandlerClass)
		CPThreadedLocalAPIServer.__init__(self, ingress_queue)

class CPUDPServer(CPThreadedLocalAPIServer, SocketServer.UDPServer):
	def __init__(self, server_address, RequestHandlerClass, ingress_queue):
		# Initialize superclass
		SocketServer.UDPServer.__init__(self, server_address, RequestHandlerClass)
		CPThreadedLocalAPIServer.__init__(self, ingress_queue)

class CPTCPServer(CPThreadedLocalAPIServer, SocketServer.TCPServer):
	def __init__(self, server_address, RequestHandlerClass, ingress_queue):
		# Initialize superclass
		SocketServer.TCPServer.__init__(self, server_address, RequestHandlerClass)
		CPThreadedLocalAPIServer.__init__(self, ingress_queue)

class CPDaemonBase:
	"""
	CreditPiggy base daemon class that implements the core logic.
	Flavored for UNIX or Windows later.
	"""

	def __init__(self, config):
		"""
		Initialize the base daemon class
		"""
		self.config = config

	def run(self):
		"""
		Entry point for the daemon class 
		"""

		# Create a logger
		logger = logging.getLogger("daemon")

		# Create a remote API server thread
		remote = CPRemoteAPIServer(self.config)
		remote_thread = threading.Thread(target=remote.run)

		# Handshake with creditpiggy to get an authentication token
		# and ensure that we can continue with the rest of initialization
		try:
			logger.info("Handshaking with CreditPiggy")
			remote.handshake()
		except Exception as e:
			logger.error("Exception %s while trying to handshake with CreditPiggy! %s" % (str(e.__class__.__name__), str(e)))
			sys.exit(1)

		# Start remote thread as a deaemon
		logger.info("Starting remote connector")
		remote_thread.daemon = True
		remote_thread.start()

		# Pick the appropriate server to start (unix,tcp,udp)
		s_type = self.config['socket'].lower()
		servers = { "unix": CPUNIXServer, "tcp": CPTCPServer, "udp": CPUDPServer }
		if not s_type in servers:
			logger.error("Invalid socket type '%s'. Expecting one of: %s" % (s_type, ",".join(servers.keys()) ) )
			sys.exit(1)

		# Get bindpoint
		s_bind = self.config['bind']
		bindpoint = []
		if s_type in ['udp', 'tcp']:

			# Split address:port
			parts = s_bind.split(":")
			if len(parts) != 2:
				logger.error("Invalid bind address configuration '%s'" % (s_bind, ) )
				sys.exit(1)

			# Create bind port
			bindpoint = (str(parts[0]), int(parts[1]))
			logger.info("Binding %s server socket on %s:%i" % (s_type.upper(), bindpoint[0], bindpoint[1]))

		else:

			# Cleanup previous socket
			if os.path.exists(s_bind) and not os.path.isfile(s_bind) and not os.path.isdir(s_bind):
				os.unlink(s_bind)

			# Bind on the next socket
			bindpoint = s_bind
			logger.info("Binding UNIX server socket on '%s'" % bindpoint)

		# Create the server, binding to the appropriate mountpoint
		local = servers[s_type]( bindpoint, CPLocalRequestHandler, remote.ingress_queue)
		local.allow_reuse_address = True
		local_thread = threading.Thread(target=local.serve_forever)

		# Start remote thread as a deaemon
		local_thread.daemon = True
		local_thread.start()

		# Register sigint handler
		def sigint_handler(signal, frame):
			"""
			Stop servers on sigint
			"""
			logger.info("Caught CTRL+C")

			# Shutdown servers
			local.shutdown()
			remote.shutdown()

			# We are now interrupted
			logger.info("Interrupted")

		# Register handler
		signal.signal(signal.SIGINT, sigint_handler)

		# Wait for the threads to exit
		localAlive = True
		remoteAlive = True
		while localAlive or remoteAlive:

			# Wait for local_tread to exit
			if not local_thread.isAlive() and localAlive:
				logger.info("Local thread exited")
				local_thread.join()
				localAlive = False

			# Wait for remote_thread to exit
			if not remote_thread.isAlive() and remoteAlive:
				logger.info("Remote thread exited")
				remote_thread.join()
				remoteAlive = False

			# Sleep a bit
			time.sleep(0.1)

		# If we had a linux socket, unlink it now
		if s_type == 'unix':
			os.unlink(bindpoint)

class CPUNIXDaemon(CPDaemonBase):

	def __init__(self, config, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
		"""
		Initialize the UNIX Daemon
		"""

		# Initialize superclass
		CPDaemonBase.__init__(self, config)
		self.config = config

		# Read configuration parameters
		self.pidfile = config['pidfile']
		self.stdin = stdin
		self.stdout = stdout
		self.stderr = stderr
   
	def daemonize(self):
		"""
		do the UNIX double-fork magic, see Stevens' "Advanced
		Programming in the UNIX Environment" for details (ISBN 0201563177)
		http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
		"""
		try:
			pid = os.fork()
			if pid > 0:
				# exit first parent
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)

		# decouple from parent environment
		os.chdir("/")
		os.setsid()
		os.umask(0)

		# do second fork
		try:
			pid = os.fork()
			if pid > 0:
				# exit from second parent
				sys.exit(0)
		except OSError, e:
			sys.stderr.write("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
			sys.exit(1)

		# redirect standard file descriptors
		sys.stdout.flush()
		sys.stderr.flush()
		si = file(self.stdin, 'r')
		so = file(self.stdout, 'a+')
		se = file(self.stderr, 'a+', 0)
		os.dup2(si.fileno(), sys.stdin.fileno())
		os.dup2(so.fileno(), sys.stdout.fileno())
		os.dup2(se.fileno(), sys.stderr.fileno())

		# write pidfile
		atexit.register(self.delpid)
		pid = str(os.getpid())
		file(self.pidfile,'w+').write("%s\n" % pid)
   
	def delpid(self):
		os.remove(self.pidfile)

	def start(self):
		"""
		Start the daemon
		"""
		# Check for a pidfile to see if the daemon already runs
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None

		if pid:
			message = "pidfile %s already exist. Daemon already running?\n"
			sys.stderr.write(message % self.pidfile)
			sys.exit(1)
	   
		# Start the daemon
		self.daemonize()
		self.run()

	def stop(self):
		"""
		Stop the daemon
		"""
		# Get the pid from the pidfile
		try:
			pf = file(self.pidfile,'r')
			pid = int(pf.read().strip())
			pf.close()
		except IOError:
			pid = None

		if not pid:
			message = "pidfile %s does not exist. Daemon not running?\n"
			sys.stderr.write(message % self.pidfile)
			return # not an error in a restart

		# Try killing the daemon process       
		try:
			# Interrupt first and give 10s grace period
			os.kill(pid, signal.SIGINT)
			for i in range(0, 100):
				os.kill(pid, 0)
				time.sleep(0.1)
			# Then terminate
			while 1:
				os.kill(pid, signal.SIGTERM)
				time.sleep(0.1)
		except OSError, err:
			err = str(err)
			if err.find("No such process") > 0:
				if os.path.exists(self.pidfile):
					os.remove(self.pidfile)
			else:
				print str(err)
				sys.exit(1)

	def restart(self):
		"""
		Restart the daemon
		"""
		self.stop()
		self.start()


if __name__ == "__main__":

	# Override config from arguments
	config_file = "creditpiggy.conf"
	for i in range(0, len(sys.argv)):
		if (sys.argv[i].startswith('--config')) or (sys.argv[i].startswith('-c')):
			if '=' in sys.argv[i]:
				# We have a '--config=' or '-c=' syntax
				parts = sys.argv[i].split('=')
				config_file = parts[1]
				del sys.argv[i]
				break
			elif i+1 >= len(sys.argv):
				print "ERROR: Missing configuration file specification"
				sys.exit(1)
			else:
				# We have a '--config <file>' or '-c <file>' syntax
				config_file = sys.argv[i+1]
				del sys.argv[i]
				del sys.argv[i]
				break

	# Make sure the config file exists
	if not os.path.exists(config_file):
		print "ERROR: The config file %s does not exist!" % config_file
		sys.exit(1)

	# Load config and defaults
	config = ConfigParser.RawConfigParser()
	config.add_section('api')
	config.set('api', 'url', 'https://creditpiggy.cern.ch/api')
	config.set('api', 'flush_interval', 5)
	config.add_section('server')
	config.set('server', 'pidfile', '/var/run/creditserver.pid')
	config.set('server', 'bind', '/var/run/creditapi.socket')
	config.set('server', 'socket', 'unix')
	config.set('server', 'loglevel', logging.INFO)
	config.set('server', 'logfile', '/dev/null')
	config.read(config_file)

	# Load all expected config parameters, so any exception is
	# thrown right now
	try:
		config = {
			'url' 			: config.get('api', 'url'),
			'project_id' 	: config.get('api', 'project_id'),
			'project_auth'	: config.get('api', 'project_auth'),
			'flush_interval': config.getint('api', 'flush_interval'),
			'pidfile' 		: config.get('server', 'pidfile'),
			'socket' 		: config.get('server', 'socket'),
			'bind' 			: config.get('server', 'bind'),
			'logfile' 		: config.get('server', 'logfile'),
			'loglevel' 		: config.getint('server', 'loglevel'),
		}
	except ConfigParser.NoSectionError as e:
		print "ERROR: Missing section '%s' in the config file '%s'" % (e.section, config_file)
		sys.exit(1)

	except ConfigParser.NoOptionError as e:
		print "ERROR: Missing option '%s' in section '%s' in the config file '%s'" % (e.option, e.section, config_file)
		sys.exit(1)

	# Setup logging
	logging.basicConfig(level=config['loglevel'], datefmt="%d-%m-%Y %H:%M:%S", format="%(asctime)s.%(msecs)04d [%(levelname)s.%(name)6s]: %(message)s")
	
	# Create a POSIX daemon if appropriate
	if os.name == 'posix':
		daemon = CPUNIXDaemon(config, stdout=config['logfile'], stderr=config['logfile'])
		if len(sys.argv) == 2:
			if 'start' == sys.argv[1]:
				daemon.start()
			elif 'stop' == sys.argv[1]:
				daemon.stop()
			elif 'restart' == sys.argv[1]:
				daemon.restart()
			else:
				print "Unknown command"
				sys.exit(2)
			sys.exit(0)
		else:
			print "usage: %s start|stop|restart [--config=|-c <config file>]" % sys.argv[0]
			sys.exit(2)

	# Otherwise just run the core logic
	else:
		daemon = CPDaemonBase(config)
		daemon.run()

