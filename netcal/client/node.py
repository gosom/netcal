#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 16:18:35
# @Last Modified by:   Giorgos Komninos
# @Last Modified time: 2013-11-10 18:03:55
import logging
import xmlrpclib
import sys
import time

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
        self.connected_nodes = []

        if self.join:
            self.log.debug('''Node should join the calendar
                           network using node: %s''', self.join)
            try:
                self.join_network()
            except Exception, e:
                sys.exit(str(e))

        self.srv = Server(service=NetCalService(), host=self.host,
                          port=self.port)
        self.srv.start()
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
        url = 'http://%s:%d' % (host, port)
        self.connected_nodes.append(self.create_proxy(url))
        self.say_hello()

    def create_proxy(self, url):
        return xmlrpclib.ServerProxy(url)

    def say_hello(self):
        proxy = self.connected_nodes[0]
        print proxy.hello()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(host='localhost', port=12345, db='mydb',
                    join=None)


