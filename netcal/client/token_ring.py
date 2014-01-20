#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
import logging
import xmlrpclib
import Queue

class TokenRing(threading.Thread):

	def __init__(self, myaddress, peers, token, req_q, res_q):
		"""Peers is the connected clients dcitionary"""
		threading.Thread.__init__(self)
		self.log = logging.getLogger(self.__class__.__name__)
		self.daemon = True
		self.kill_received = False
		self.myaddress = myaddress
		self.peers = peers
		self.wait_time = 1.0
		self.token = token
		self.commands = req_q
		self.results = res_q

	def run(self):
		self.log.debug('Starting TokenRing Thread with token: %s', str(self.token))
		while not self.kill_received:
			if self.token:
				#self.log.debug('Proxy is mine')
				try:
					command = self.commands.get(block=False)
				except Queue.Empty:
					pass
				except Exception as e:
					self.log.exception(str(e))
				else:
					self.log.debug('RECEIVED %d', len(command))
					to_execute = []
					for p, func_name, args in command:
						self.log.debug('Executing %s for %s', func_name,
							repr(p))
						func = getattr(p, func_name)
						to_execute.append((func, args))
					res = [f(*a) for f, a in to_execute]
					self.results.put(all([True if r == 0 else False for r in res]))
					self.commands.task_done()
				time.sleep(10)
				self.token = False
				self.forward_token()
			time.sleep(self.wait_time)


	def forward_token(self):
		next_address = self.next_peer()
		#self.log.debug('We should forward the token to next: %s',
		#	next_address)
		target_list = next_address.split(':')
		host, port = target_list[0], int(target_list[1])
		url = 'http://%s:%d' % (host, port)
		#self.log.debug('Creating proxy: %s', url)
		proxy =  xmlrpclib.ServerProxy(url,allow_none=True)
		proxy.handler1.tokenReceived(self.myaddress)


	def next_peer(self):
		"""returns the address of the next peer"""
		addresses = self.peers.keys()
		next_i = (addresses.index(self.myaddress)+1)%len(addresses)
		return addresses[next_i]
