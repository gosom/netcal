#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-10 11:58:37
# @Last Modified by:   Giorgos Komninos
# @Last Modified time: 2013-11-10 16:08:43
import logging
from SimpleXMLRPCServer import SimpleXMLRPCServer
import threading


class Server(threading.Thread):
    """Subclassing Thread"""

    def __init__(self, service, host='localhost', port=12345):
        """Parameters:
        : service : An object to expose it's methods
        : host : the host the xml-rpc server will run - optional
        : port : the port the xml-rpc server"""
        threading.Thread.__init__(self)
        self.log = logging.getLogger(self.__class__.__name__)
        self.daemon = True
        self.log.debug('Starting xml-rpc server')
        assert port in xrange(0, 65535)
        self.srv = SimpleXMLRPCServer((host, port),
                                      logRequests=True)
        self.srv.register_instance(service)
        self.kill_received = False
        self.log.debug('Server is ready')

    def run(self):
        self.log.debug('Starting serving')
        while not self.kill_received:
            self.srv.handle_request()
        self.log.debug('Server was terminated')


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    from services import NetCalService

    server = Server(service=NetCalService())
    server.start()
    while server.isAlive():
        try:
            pass
        except KeyboardInterrupt:
            print 'Ctrl-C received'
            server.kill_received = True
