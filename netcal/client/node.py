#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 16:18:35
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-18 18:53:51
import logging
import xmlrpclib
import sys
import time
import atexit

from netcal.srv.server import Server
from netcal.srv.services import NetCalService
import netcal.utils as utils
from netcal.dbo.db import DB

class Node(object):

    def __init__(self, my_address, db):
        """Node object.
        Parameters:
        :my_address : ip:port
        :db : the sqlite file to store local database
        """
        self.log = logging.getLogger(self.__class__.__name__)
        self.log.debug('Initializing Node')
        self.my_address = my_address
        self.db = DB(fname=db)
        self.my_host, self.my_port = self.get_host_port(self.my_address)
        self.connected_clients = {}
        self.connected_clients[self.my_address] = None # we are connected

        # here we maintain a list of proxy objects.
        # the len(proxies) = len(connected_clients)-1,
        # since we do not need proxy for our instance
        self.proxies = []
        atexit.register(self.leave) # signoff when program terminates

        # start a new thread for the server
        self.log.debug('Starting server')
        self.srv = Server(service=NetCalService(self.connected_clients,
                                                db),
                          host=self.my_host,
                          port=self.my_port,)
        self.srv.start()

    def connect(self, address):
        """method to join the calendar network.
        First it fetches the client list from address
        Then it signins to very client
        and finally synchronizes the db from address
        Parameters
        :addess : the remote address i.e. ip:port"""
        self.log.debug('Attempting to connect to %s', address)
        # TODO validate address
        try:
            self.connected_clients[address] = self.create_proxy(address)
            proxy = self.get_proxy(address)
            clients_list = proxy.get_clients()
            self.log.debug('We got %d clients', len(clients_list))
            for c_address in clients_list:
                if c_address not in self.connected_clients:
                    self.log.debug('Adding %s to connected_clients', c_address)
                    self.connected_clients[c_address] = None
            for address in self.connected_clients:
                proxy = self.get_proxy(address)
                proxy.signin(self.my_address)
            upd_ts = self.db.get_max_timestamp()
            if upd_ts is None:
                upd_ts = ''
            upd_rows = proxy.pull(self.my_address, upd_ts)
            if upd_rows:
               self.log.debug('we got %d updated rows', len(upd_rows))
               self.db.apply_updates(upd_rows)
               self.log.debug('succesfully updated db')
            return True
        except:
            self.log.exception('An exception occured while attempting to connect')
            return False

    def leave(self):
        for a in self.connected_clients:
            if a != self.my_address:
                p = self.get_proxy(a)
                p.sign_off(self.my_address)
        self.log.debug('Node left network')

    def add(self, date_time, duration, header, comment):
        '''adds an appointment to the database and propagates
        the appointment to the connected_clients'''
        try:
            self.db.insert(dt=date_time, dur=duration, he=header, com=comment)
        except Exception:
            self.log.error('cannot insert appointment: %s %s %s %s',
                           date_time, duration, header, comment)
            return False
        else:
            self.log.debug('appointment %s %s was added', date_time, header)
            return True

    def list(self):
        '''returns a list with all appointments'''
        try:
            to_return = self.db.get_all()
        except:
            self.log.exception('cannot get list from database')
            return False
        else:
            return to_return

    def create_proxy(self, address):
        """Creates a proxy object for the address"""
        host, port = self.get_host_port(address)
        assert utils.check_connection(host, port) == True
        url = 'http://%s:%d' % (host, port)
        self.log.debug('Creating proxy: %s', url)
        return xmlrpclib.ServerProxy(url)

    def get_proxy(self, address):
        if self.connected_clients[address] is None:
            self.connected_clients[address] = self.create_proxy(address)
        return self.connected_clients[address]

    def get_host_port(self, address):
        target_list = address.split(':')
        host, port = target_list[0], int(target_list[1])
        return host, port



if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(my_address='localhost:12345', db='mydb',)


