#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 16:18:35
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 08:36:50
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
        self.connected = False

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
            init_address = address
            self.connected_clients[init_address] = self.create_proxy(init_address)
            proxy = self.get_proxy(init_address)
            clients_list = proxy.get_clients()
            self.log.debug('We got %d clients', len(clients_list))
            for c_address in clients_list:
                if c_address not in self.connected_clients:
                    self.log.debug('Adding %s to connected_clients', c_address)
                    self.connected_clients[c_address] = None
            for p in self.proxy_gen():
                p.signin(self.my_address)
            if self.sync(init_address):
                return True
            else:
                raise Exception('cannot sync')
        except:
            self.log.exception('An exception occured while attempting to connect')
            return False

    # core methods

    def sync(self, address):
        self.log.debug('sync with %s', address)
        if address not in self.connected_clients:
            self.log.error('%s not in connected clients')
            return False
        proxy = self.get_proxy(address)
        upd_ts = self.db.get_max_timestamp()
        if upd_ts is None:
            upd_ts = ''
        upd_rows = proxy.pull(self.my_address, upd_ts)
        if upd_rows:
               self.log.debug('we got %d updated rows', len(upd_rows))
               self.db.apply_updates(upd_rows)
               self.log.debug('succesfully updated db')
        return True

    def leave(self):
        self.connected = False
        for p in self.proxy_gen():
                p.sign_off(self.my_address)
        self.log.debug('Node left network')

    def add(self, date_time, duration, header, comment):
        '''adds an appointment to the database and propagates
        the appointment to the connected_clients'''
        item = self.srv.service.add(date_time, duration, header, comment, None,
                                    None)
        if not item:
            self.log.error('cannot add to database')
            return False
        else:
            for p in self.proxy_gen():
                p.add(date_time, duration, header, comment, item['uid'],
                      item['last_modified'])
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

    def delete(self, uid):
        '''deletes the row with uid'''
        if not self.srv.service.delete(uid):
            self.log.error('cannot delete row with id %s', uid)
            to_return = None
        else:
            for p in self.proxy_gen():
                p.delete(uid)
            return True

    def edit(self, uid, fields_to_edit):
        '''updates the row with uid with values from fields to edit'''
        self.log.debug('Editing appointment with uid %s', uid)
        item = self.srv.service.edit(uid, fields_to_edit)
        if not item:
            self.log.error('Cannot edit database')
            return False
        else:
            fields_to_edit['last_modified'] = item['last_modified']
            for p in self.proxy_gen():
                p.edit(uid, fields_to_edit)
            return True

    def view(self, uid):
        self.log.debug('Returns appointment with id uid')
        try:
            item = self.db.get(uid)
        except:
            self.log.exception('Exsception while getting appointment')
            return None
        else:
            return item

    # helper methods

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

    def proxy_gen(self):
        """generates proxies"""
        for a in self.connected_clients:
            if a != self.my_address:
                proxy = self.get_proxy(a)
                yield proxy

    def is_connected(func):
        if not self.connected:
            return False
        def inner(*args, **kwargs):
            return func(*args, **kwargs)
        return inner


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(my_address='localhost:12345', db='mydb',)


