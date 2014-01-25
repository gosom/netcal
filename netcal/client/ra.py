#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import logging
import Queue
import xmlrpclib
import time

from netcal.client.lamport import LamportClock


class Ra(threading.Thread):

    def __init__(self,node, command_queue, results_queue):
        threading.Thread.__init__(self,)
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Starting Ra thread')
        self.node = node
        self.daemon = True
        self.command_queue = command_queue
        self.results = results_queue

        self.kill = False

    def run(self):
        while not self.kill:
            try:
                item = self.command_queue.get(block=False)
            except Queue.Empty:
                time.sleep(0.1)
                continue
            #self.log.debug('Received %s', str(item))
            if isinstance(item, basestring):
                pass
            elif isinstance(item, (tuple, list)):
                if item[0] == 'CS':
                    command, resource_id, own_id, clock = item
                    #self.log.debug('Command is CS')
                    for address in self.node.connected_clients:
                        p = self.create_proxy(address)
                        p.hanler1.csRequestReceived(resource_id, own_id, clock)
                elif item[0] == 'SO':
                    #self.log.debug('Sending OK')
                    command, hosts = item
                    for address in hosts:
                        p = self.create_proxy(address)
                        p.handler1.replyReceived(self.node.my_address)
            self.command_queue.task_done()

    def create_proxy(self, address):
        #self.log.debug('Creating proxy for %s', address)
        target_list = address.split(':')
        host, port = target_list[0], int(target_list[1])
        url = 'http://%s:%d' % (host, port)
        proxy =  xmlrpclib.ServerProxy(url,allow_none=True)
        return proxy
