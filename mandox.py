#!/usr/bin/python

""" 
  The polyglot persistence UI.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2013-06-23
@status: init
"""
import sys
import os
import logging
import getopt
import urlparse
import urllib
import string
import cgi
import time
import datetime
import json
import socket
import subprocess
import re

from BaseHTTPServer import BaseHTTPRequestHandler
from os import curdir, sep

DEBUG = False

# The default ports to be scanned for active services.
#
# If no '.mandox_config' file exists in the current directory, then these 
# values  below are used as defaults.
#
# NOTE: the format of the config file '.mandox_config' is a new-line
#       separated list of entries (lines starting with a '#' are ignored),
#       each of the following form:
#
#       SERVICE:START_PORT-END_PORT
#
#       Remember that the START_PORT is included and the END_PORT is excluded.
#       For example, to scan service ABC on port 8080 you would supply the
#       following in the config file:
#
#       ABC:8080-8081
#
service_to_port_range = { 
	'HDFS'   : '50070-50076',
	'HBase1' : '60010-60031',
	'HBase2' : '8080-8081',
	'Hive1'  : '10000-10001',
	'Hive2'  : '9083-9084',
	'MongoDB': '28017-28018',
	'CouchDB': '5984-5985',
	'Riak'   : '8091-8092'
}

if DEBUG:
	FORMAT = '%(asctime)-0s %(levelname)s %(message)s [at line %(lineno)d]'
	logging.basicConfig(level=logging.DEBUG, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')
else:
	FORMAT = '%(asctime)-0s %(message)s'
	logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt='%Y-%m-%dT%I:%M:%S')


# the main mandox service
class MandoxServer(BaseHTTPRequestHandler):
	
	# reacts to GET request by serving static content in standalone mode 
	# and handles API calls to deal with datasources
	def do_GET(self):
		parsed_path = urlparse.urlparse(self.path)
		target_url = parsed_path.path[1:]
		
		# API calls
		if self.path.startswith('/ds/'):
			self.serve_api(self.path)
		# static stuff (for standalone mode - typically served by Apache or nginx)
		elif self.path == '/':
			self.serve_static_content('index.html')
		elif self.path.endswith('.ico'):
			self.serve_static_content(target_url, media_type='image/x-icon')
		elif self.path.endswith('.html'):
			self.serve_static_content(target_url, media_type='text/html')
		elif self.path.endswith('.js'):
			self.serve_static_content(target_url, media_type='application/javascript')
		elif self.path.endswith('.css'):
			self.serve_static_content(target_url, media_type='text/css')
		elif self.path.startswith('/img/'):
			if self.path.endswith('.gif'):
				self.serve_static_content(target_url, media_type='image/gif')
			elif self.path.endswith('.png'):
				self.serve_static_content(target_url, media_type='image/png')
			else:
				self.send_error(404,'File Not Found: %s' % target_url)
		else:
			self.send_error(404,'File Not Found: %s' % target_url)
		return
	
	# serves an API call
	def serve_api(self, apicall):
		logging.info('API call: %s ' %(apicall))
		if apicall == '/ds/':
			logging.debug(' current list of discovered datasources')
		elif apicall.startswith('/ds/scan/'):
			logging.debug(' scanning datasources')
			
			# either a from/to range as in 192.122.143.48-192.122.143.55 
			# or a comma-separated list as in n1.example.org,n2.example.org 
			host_range = apicall.split('/')[-1]

			if not host_range: # default to scanning the localhost
				logging.debug('  scanning localhost')
				self.scan_hosts('127.0.0.1-127.0.0.1')
			elif ('-' in host_range) or (',' in host_range):
				logging.debug('  host range: %s' %(host_range))
				self.scan_hosts(host_range)
			else: 
				self.send_error(404,'File Not Found: %s' % apicall)
		else:
			self.send_error(404,'File Not Found: %s' % apicall)
		return
	
	# changes the default behavour of logging everything - only in DEBUG mode
	def log_message(self, format, *args):
		if DEBUG:
			try:
				BaseHTTPRequestHandler.log_message(self, format, *args)
			except IOError:
				pass
		else:
			return
	
	# serves static content from file system
	def serve_static_content(self, p, media_type='text/html'):
		try:
			f = open(curdir + sep + p)
			self.send_response(200)
			self.send_header('Content-type', media_type)
			self.end_headers()
			self.wfile.write(f.read())
			f.close()
			return
		except IOError:
			self.send_error(404,'File Not Found: %s' % self.path)
	
	# scans a range of hosts for active ports. 
	# output: map of host/IPs to open ports as in {"127.0.0.1": [50070, 50075]}
	# NOTE: the from/to range is for IPs only (currently not checking if IPs are supplied)
	# whilst the comma-separated list works for both hostnames or IP addresses.
	def scan_hosts(self, host_range):
		if '-' in host_range: # from/to IP range as in 192.122.143.48-192.122.143.55 
			start_IP = host_range.split('-')[0]
			end_IP = host_range.split('-')[1]
			# NOTE: I should really check if a valid IP range has been supplied!
			host_list = self.gen_IP_range(start_IP, end_IP)
		else: # a comma-separated list as in n1.example.org,n2.example.org 
			host_list = [h for h in host_range.split(',')]
		
		try: # scan the target hosts and create a dict from host/IP to open ports
			results = {}
			for target_host in host_list:
				if target_host:
					open_ports = []
					for service in sorted(service_to_port_range): # scan all port ranges
						logging.debug('   now checking for service %s in port range %s' %(service, service_to_port_range[service]))
						start_port = int(service_to_port_range[service].split('-')[0])
						end_port = int(service_to_port_range[service].split('-')[1])
						open_ports.extend(self.scan_services(target_host, start_port, end_port))
					results[target_host] = open_ports
			self.send_response(200)
			self.send_header('Content-type', 'application/json')
			self.end_headers()
			logging.info('Success: %s ' %(results))
			self.wfile.write(json.dumps(results))
		except:
			logging.info('Server error while scanning hosts %s' %host_range)
			self.send_error(500, 'Server error while scanning hosts %s' %host_range)
		
	
	# generates a list of IP addresses based on an IP range
	# lifted from http://cmikavac.net/2011/09/11/how-to-generate-an-ip-range-list-in-python/
	def gen_IP_range(self, start_IP, end_IP):
		start = list(map(int, start_IP.split(".")))
		end = list(map(int, end_IP.split(".")))
		temp = start
		ip_range = []
		ip_range.append(start_IP)
		while temp != end:
			start[3] += 1
			for i in (3, 2, 1):
				if temp[i] == 256:
					temp[i] = 0
					temp[i-1] += 1
			ip_range.append(".".join(map(str, temp)))
		return ip_range
	
	# scans services via testing open ports on a given host.
	# the host address can be a valid DNS name (like example.org) 
	# or an IP address (such as 127.0.0.1)
	def scan_services(self, target_host, start_port, end_port):
		# the result is a list of open ports of supplied target host 
		open_ports = []
		
		# make sure we're dealing with an IP address,
		# so if a host name has been provided turn it
		# into a valid IP address.
		is_IP_address = re.match("^(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])$", target_host)
		if is_IP_address:
			target_IP  = target_host
		else:
			target_IP  = socket.gethostbyname(target_host)
		
		subprocess.call('clear', shell=True)
		logging.debug('   scanning %s ...' %target_host)
		
		# scan the ports of the given target IP and report on open ports
		try:
			for port in range(start_port, end_port):  
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				result = sock.connect_ex((target_IP, port))
				if result == 0:
					logging.debug('    found open port %d on host %s' %(port, target_IP))
					open_ports.append(port)
				sock.close()
		except socket.gaierror:
			logging.info('    can\'t resolve %s' %target_host)
		except socket.error:
			logging.info('    can\'t connect to %s' %target_host)
		
		return open_ports
	
def usage():
	print("Usage: python mandox.py")

# expecting the config file '.mandox_config' in the same directory as 
# the script is launched, otherwise using default values
def read_config():
	if os.path.exists('.mandox_config'):	
		lines = tuple(open('.mandox_config', 'r'))
		service_to_port_range = {}
		for line in lines:
			l = str(line)
			if not l.startswith('#'):
				service = line.split(':')[0]
				port_range = str(line.split(':')[1]).rstrip()
				service_to_port_range[service] = port_range
		logging.info('Found mandox config file ...')
	else:
		logging.info('No mandox config file found, using defaults.')
		
	logging.info('Using the following ports for scanning:')
	for service in sorted(service_to_port_range):
		logging.info(' %s: %s' %(service, service_to_port_range[service]))


if __name__ == '__main__':
	print("="*80)
	read_config()
	print("="*80)
	try:
		# extract and validate options and their arguments
		opts, args = getopt.getopt(sys.argv[1:], 'hv', ['help','verbose'])
		for opt, arg in opts:
			if opt in ('-h', '--help'):
				usage()
				sys.exit()
			elif opt in ('-v', '--verbose'): 
				DEBUG = True
		from BaseHTTPServer import HTTPServer
		server = HTTPServer(('', 6543), MandoxServer)
		print('\nmandox server started, use {Ctrl+C} to shut-down ...')
		server.serve_forever()
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)	
	