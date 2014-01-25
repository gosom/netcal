#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import time
import logging
import xmlrpclib
import Queue

class TokenRing(threading.Thread):

	def __init__(self, myaddress, peers, req_q, res_q):
		"""Peers is the connected clients dcitionary"""
		threading.Thread.__init__(self)
		self.log = logging.getLogger(self.__class__.__name__)
		self.daemon = True
		self.kill_received = False
		self.myaddress = myaddress
		self.peers = peers
		self.wait_time = 1
		self.token = False
		self.commands = req_q
		self.results = res_q
		self.signin_q = Queue.Queue()

	def run(self):
		self.log.debug('Starting TokenRing Thread with token: %s', str(self.token))
		while not self.kill_received:
			if self.token:
				#self.log.debug('Proxy is mine')
				#next_address = self.next_peer()
				#self.log.debug('Next peer is %s', next_address)
				self.consume_command_queue()
				self.consume_signin_queue()
				time.sleep(self.wait_time)
				#self.log.debug('Peers : %s', str(self.peers))
				if len(self.peers) > 1:
					self.token = False
					self.forward_token()
			else:
				time.sleep(self.wait_time)
		self.log.debug('Token ring thread is terminating')

	def consume_signin_queue(self):
		while True:
			try:
				address = self.signin_q.get(block=False)
			except Queue.Empty:
				break
			except Exception as e:
				self.log.exception(str(e))
			else:
				self.log.debug('Got command %s from siginqueue', str(address))
				proxy = self.create_proxy(address)
				proxy.handler1.signInApproved(self.myaddress)
				self.log.debug('Executed signInApproved from %s', address)

	def consume_command_queue(self):
		try:
			command = self.commands.get(block=False)
		except Queue.Empty:
			pass
		except Exception as e:
			self.log.exception(str(e))
		else:
			if not isinstance(command, basestring):
				self.log.debug('RECEIVED %d', len(command))
				to_execute = []
				for item in command:
					p, command_dict = item
					self.log.debug('Executing for proxy: %s', repr(p))
					self.log.debug(str(command_dict))
					while command_dict:
						func_name, args = command_dict.popitem(False)
						func = getattr(p, func_name)
						to_execute.append((func, args))
						self.log.debug('Added %s for execution', func_name)
				res = [f(*a) for f, a in to_execute]
				self.results.put(res)
				self.commands.task_done()
			elif command == 'PAUSE':
				self.log.debug('Received PAUSE command')
				self.results.put('OK')
				self.commands.task_done()
				release = self.commands.get(block=True)
				if release != 'RELEASE':
					self.log.critical('After pause you should send RELEASE')
				else:
					self.log.debug('Releasing token')
					self.results.put('OK')
				self.commands.task_done()


	def forward_token(self, next_address=None):
		if not next_address:
			next_address = self.next_peer()
		if next_address:
			#self.log.debug('We should forward the token to next: %s',
			#	next_address)
			proxy =  self.create_proxy(next_address)
			try:
				proxy.handler1.tokenReceived(self.myaddress)
			except Exception as e:
				self.log.exception(str(e))
		else:
			self.log.debug('Nothing to forward')

	def create_proxy(self, address):
		#self.log.debug('Creating proxy for %s', address)
		target_list = address.split(':')
		host, port = target_list[0], int(target_list[1])
		url = 'http://%s:%d' % (host, port)
		proxy =  xmlrpclib.ServerProxy(url,allow_none=True)
		return proxy

	def next_peer(self):
		"""returns the address of the next peer"""
		addresses = self.peers.keys()
		next_i = (addresses.index(self.myaddress)+1)%len(addresses)
		try:
			nxt_ad = addresses[next_i]
		except IndexError:
			nxt_ad = None
		return nxt_ad



