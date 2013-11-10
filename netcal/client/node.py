#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 16:18:35
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-10 22:46:43
import logging
import xmlrpclib
import sys
import time
import atexit

from netcal.srv.server import Server
from netcal.srv.services import NetCalService
import netcal.utils as utils

class Node(object):

    def __init__(self, host, port, db, join=None):
        """Node object.
        Parameters:
        :host : hostname
        :port : port to start server
        :join : ip:port to connect - default None
        :db : the sqlite file to store local database
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initializing Node')
        self.host, self.port = host, port
        self.db = None
        self.join = join
        self.proxies = []
        atexit.register(self.leave) # signoff when program terminates
        self.srv = Server(service=NetCalService([(self.host, self.port)]),
                          host=self.host,
                          port=self.port)
        self.srv.start()

        if self.join:
            
            self.log.debug('''Node should join the calendar
                           network using node: %s''', self.join)
            try:
                self.join_network()
            except Exception, e:
                sys.exit(str(e))

        while True:
            try:
                time.sleep(0.2)
            except KeyboardInterrupt:
                self.log.debug('Terminating')
                break

    def join_network(self, ):
        """method to join the calendar network.
        Node says HELLO to the host specified in self.join,
        and retrieves a snapshot of the database & a
        list of clients"""
        target_list = self.join.split(':')
        host, port = target_list[0], int(target_list[1])
        assert utils.check_connection(host, port) == True
        self.proxies.append(self.create_proxy(host, port))
        self.say_hello(host, port)
        self.synchronize(host, port)

    def create_proxy(self, host, port):
        url = 'http://%s:%d' % (host, port)
        self.log.debug('Creating proxy: %s', url)
        return xmlrpclib.ServerProxy(url)

    def say_hello(self, to_host, to_port):
        """says hello to host:port"""
        self.srv.connected_clients = self.proxies[0].hello()
        self.log.debug('We got %d connected_clients', 
                       len(self.srv.connected_clients))
        for host, port in self.srv.connected_clients:
            if host != to_host and port != to_port:
                self.proxies.append(create_proxy(host, port))

    def synchronize(self, from_host, from_port):
        snapshot = self.proxies[0].pull(self.host, self.port)
        print snapshot

    def leave(self):
        for p in self.proxies:
            p.sign_off(self.host, self.port)
        self.log.debug('Node left network')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(host='localhost', port=12345, db='mydb',
                    join=None)


