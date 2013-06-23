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
