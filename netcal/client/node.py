#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import xmlrpclib
import sys
import time
import atexit
from collections import OrderedDict
import threading
from copy import deepcopy
import Queue


import netcal.utils as utils
from netcal.dbo.db import DB

from netcal.srv.server import Server
from netcal.srv.services import NetCalService


class Node(object):

    def __init__(self, my_address, db, **kwargs):
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

        self.connected_clients = OrderedDict()
        self.connected_clients[self.my_address] = None
        self.connected = False

        # here we maintain a list of proxy objects.
        # the len(proxies) = len(connected_clients)-1,
        # since we do not need proxy for our instance
        self.proxies = []
        atexit.register(self.leave) # signoff when program terminates

        #mutual exclusion algs
        self.use_token_ring = kwargs.get('token_ring', False)
        self.use_ra = False

        if self.use_token_ring:
            self.__init_token_ring()

        # start a new thread for the server
        self.log.debug('Starting server')
        self.srv = Server(service=NetCalService(node=self,
                                                connected_clients=self.connected_clients,
                                                db_name=db,),
                          host=self.my_host,
                          port=self.my_port)
        self.srv.start()

    def __init_token_ring(self,):
        self.log.debug('Initializing token ring')
        from netcal.client.token_ring import TokenRing
        self.request_queue = Queue.Queue()
        self.result_queue = Queue.Queue()
        self.token_ring = TokenRing(myaddress=self.my_address,
                                        peers=self.connected_clients,
                                        token=False,
                                        req_q=self.request_queue,
                                        res_q=self.result_queue)



    def signin(self, address):
        self.log.debug('Doing actual signin')
        #self.connected_clients[address] = self.create_proxy(address)
        proxy = self.create_proxy(address)
        clients_list = proxy.handler1.get_clients(self.my_address)
        #proxy.handler1.signin(self.my_address)
        for c_address in clients_list:
            self.log.debug('Adding %s to connected_clients', c_address)
            self.connected_clients[c_address] = None
        if self.my_address not in self.connected_clients:
            self.connected_clients[self.my_address] = None
        for p in self.proxy_gen(exclude=[self.my_address,]): # do not signin to me and master
            p.handler1.signin(self.my_address)
        self.sync(address)

        self.connected = True

    def connect(self, address):
        """method to join the calendar network.
        First it fetches the client list from address
        Then it signins to very client
        and finally synchronizes the db from address
        Parameters
        :addess : the remote address i.e. ip:port"""
        self.log.debug('Attempting to connect to %s', address)
        # TODO validate address
        ret_value = False

        # first signin to address in order to get the proxy
        init_address = address
        self.connected_clients.clear()
        self.connected_clients[init_address] = self.create_proxy(init_address)
        proxy = self.get_proxy(init_address)
        if self.use_token_ring:
            self.connected_clients.clear()
            if not address or address.lower() == self.my_address.lower():
                self.connected_clients[self.my_address] = None
                self.connected = True
                self.token_ring.token = True
            else:
                self.log.debug('Doing requestSignin')
                proxy.handler1.requestClientSignIn(self.my_address)
            self.token_ring.start()
            ret_value = True
        else:
            raise NotImplementedError
        while not self.connected:
            time.sleep(0.1)
        return ret_value

    # core methods
    def get_connected_clients(self):
        return self.connected_clients.keys()

    def sync(self, address):
        """synchronizes the local database with the one of
        address.
        Parameters:
        :param address: the address (ip:port) of the remote host
        returns: True on success else False
        """
        self.log.debug('sync with %s', address)
        if address not in self.connected_clients:
            self.log.error('%s not in connected clients')
            return False
        proxy = self.get_proxy(address)
        upd_rows = proxy.handler1.getTableData(self.my_address)
        if upd_rows:
               self.log.debug('we got %d updated rows', len(upd_rows))
               self.db.apply_updates(upd_rows) # # # # #
               self.log.debug('succesfully updated db')
        return True

    def leave(self):
        """leaves the network"""
        if not self.connected:
            self.log.debug('You are not connected. Exititing')
        else:
            if self.use_token_ring:
                self.send_pause()
                self.token_ring.kill_received = True
                next_address = self.token_ring.next_peer()
                for p in self.proxy_gen(exclude=[self.my_address,]):
                    p.handler1.sign_off(self.my_address)
                self.send_release()
                self.token_ring.forward_token(next_address=next_address)
            else:
                for p in self.proxy_gen(exclude=[self.my_address]):
                    p.handler1.sign_off(*func_args)
            self.connected = False
        self.log.debug('Node left network')

    def add(self, date, time, duration, header, comment):
        '''adds an appointment to the database and propagates
        the appointment to the connected_clients'''
        if self.use_token_ring:
            func_args = (int(1), int(0), date, time, duration, header, comment)
            cmd_dict = OrderedDict()
            cmd_dict["handler1.functionsToPerform"] =  func_args
            self.__execute_token_ring_cmd(cmd_dict)
        else:
            for p in self.proxy_gen():
                p.handler1.addRowClient(date, time, duration, header, comment)
        return int(0)

    def list(self):
        '''returns a list with all appointments'''
        try:
            to_return = self.db.get_all()
        except:
            self.log.exception('cannot get list from database')
            return False
        else:
            return to_return

    def delete_all(self):
        '''deletes all row'''
        if not self.srv.service.delete_all():
            self.log.error('cannot delete')
            to_return = None

    def delRowClient(self, uid):
        '''deletes the row with uid'''
        self.log.debug('Deleting appointment with uid %s', uid)
        if self.use_token_ring:
            func_args = (int(2), int(uid), '', '', '', '', '')
            cmd_dict = OrderedDict()
            cmd_dict["handler1.functionsToPerform"] =  func_args
            self.__execute_token_ring_cmd(cmd_dict)
        else:
            for p in self.proxy_gen():
                p.handler1.delRowClient(uid)
        return True

    def edit(self, uid, date, time, duration, header, comment):
        """updates the row with uid with values from fields to edit"""
        self.log.debug('Editing appointment with uid %s', uid)
        if self.use_token_ring:
            func_args = (int(3), int(uid), date, time, duration, header, comment)
            cmd_dict = OrderedDict()
            cmd_dict["handler1.functionsToPerform"] =  func_args
            self.__execute_token_ring_cmd(cmd_dict)
        else:
            for p in self.proxy_gen():
                p.handler1.editRowClient(uid, date, time, duration, header, comment)
        return True

    def view(self, uid):
        """Returns appointment with id uid"""
        try:
            item = self.db.get(uid)
        except:
            self.log.exception('Exsception while getting appointment')
            return None
        else:
            return item

    # helper methods

    def __execute_token_ring_cmd(self, cmd_name_dict, exclude=[]):
        command = []
        self.log.debug('Putting %s command to queue', str(cmd_name_dict))
        for p in self.proxy_gen(exclude=exclude):
            tmp_dict = deepcopy(cmd_name_dict)
            command.append((p, tmp_dict))
        self.request_queue.put(command)
        while True:
            self.log.debug('waiting token')
            results = self.result_queue.get(block=True)
            self.result_queue.task_done()
            break
        self.log.debug('Completed %s', cmd_name_dict)

    def create_proxy(self, address):
        """Creates a proxy object for the address"""
        host, port = self.get_host_port(address)
        assert utils.check_connection(host, port) == True
        url = 'http://%s:%d' % (host, port)
        self.log.debug('Creating proxy: %s', url)
        return xmlrpclib.ServerProxy(url,allow_none=True)

    def get_proxy(self, address):
        """return a proxy for address. If does not exists it creates it"""
        if self.connected_clients[address] is None:
            self.connected_clients[address] = self.create_proxy(address)
        return self.connected_clients[address]

    def get_host_port(self, address):
        """returns the host and the port of an address of the from ip:port"""
        target_list = address.split(':')
        host, port = target_list[0], int(target_list[1])
        return host, port

    def proxy_gen(self, exclude=[]):
        """generates proxies"""
        for a in self.connected_clients:
            if a not in exclude:
                proxy = self.get_proxy(a)
                yield proxy

    def send_pause(self):
        self.log.debug('Sending PAUSE command')
        self.request_queue.put("PAUSE")
        res = self.result_queue.get(block=True)
        self.result_queue.task_done()

    def send_release(self):
        self.log.debug('Sending RELEASE command')
        self.request_queue.put('RELEASE')
        res = self.result_queue.get(block=True)
        self.result_queue.task_done()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(my_address='localhost:12345', db='mydb',)


