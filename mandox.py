#!/usr/bin/python

""" 
  The polyglot persistence UI.

@author: Michael Hausenblas, http://mhausenblas.info/#i
@since: 2013-06-23
@status: init
"""
import sys
import logging
import getopt
import StringIO
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

# configuration
DEBUG = True

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
		if self.path.startswith('/ds'):
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
		logging.debug('API call: %s ' %(apicall))
		if apicall == '/ds':
			logging.debug('API call: current list of discovered datasources')
		elif apicall == '/ds/scan':
			logging.debug('API call: scanning datasources')
			try:
				open_ports =  self.scan_services('127.0.0.1', 50068, 50080)
				self.send_response(200)
				self.send_header('Content-type', 'application/json')
				self.end_headers()
				self.wfile.write(json.dumps(open_ports))
			except:
				self.send_error(500, 'Server error while scanning datasources.')
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
	
	# scans services via testing open ports.
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
		logging.debug('Scanning %s ...' %target_host)
		
		# scan the ports of the given target IP and report on open ports
		try:
			for port in range(start_port, end_port):  
				sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				result = sock.connect_ex((target_IP, port))
				if result == 0:
					logging.debug(' found open port %d on host %s' %(port, target_IP))
					open_ports.append(port)
				sock.close()
		except socket.gaierror:
			logging.info('Can\'t resolve %s' %target_host)
		except socket.error:
			logging.info('Can\'t connect to %s' %target_host)
		
		return open_ports

def usage():
	print("Usage: python mandox.py")

if __name__ == '__main__':
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
		logging.info('mandox server started, use {Ctrl+C} to shut-down ...')
		server.serve_forever()
	except getopt.GetoptError, err:
		print str(err)
		usage()
		sys.exit(2)	
