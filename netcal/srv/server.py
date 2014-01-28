#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
        self.service = service
        self.srv = SimpleXMLRPCServer((host, port),allow_none=True,
                                      logRequests=False)
        self.srv.register_instance(self.service)

        self.srv.register_function(service.get_clients, 'handler1.get_clients')
        self.srv.register_function(service.signin, 'handler1.signin')
        self.srv.register_function(service.rclient_signin, 'handler1.requestClientSignIn')
        self.srv.register_function(service.sign_off, 'handler1.sign_off')
        self.srv.register_function(service.getTableData, 'handler1.getTableData') #pull
        self.srv.register_function(service.addRowClient, 'handler1.addRowClient')
        self.srv.register_function(service.editRowClient, 'handler1.editRowClient')
        self.srv.register_function(service.delRowClient, 'handler1.delRowClient')
        self.srv.register_function(service.tokenReceived, 'handler1.tokenReceived')
        self.srv.register_function(service.sign_in_approved, 'handler1.signInApproved')
        self.srv.register_function(service.function_to_perform, 'handler1.functionsToPerform')
        self.srv.register_function(service.cs_request_received, 'handler1.csRequestReceived')
        self.srv.register_function(service.reply_received, 'handler1.replyReceived')

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
