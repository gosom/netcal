#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 12:27:46
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-10 22:44:51
import logging
import os

class NetCalService(object):
    """Here are all the functions we want to
    expose via xml-rpc"""

    def __init__(self, connected_clients=[]):
        self.log = logging.getLogger(self.__class__.__name__)
        self.connected_clients = connected_clients

    def hello(self,):
        self.log.debug('Calling hello method')
        self.log.debug('returning %s', str(self.connected_clients))
        return self.connected_clients

    def list(self, dir_name):
        """This is a demo funtion for testing purposes.
        It returns a list of the files in dir_name"""
        self.log.debug('Calling list method')
        return os.listdir(dir_name)

    def pull(self, host, port):
        """pull function returns a snapshot of the database"""
        item = (host, port)
        if item not in self.connected_clients:
            self.connected_clients.append(item)
            self.log.debug('Added %s to connected_clients', str(item))
        return 'OK'

    def sign_off(self, host, port):
        item = (host, port)
        self.connected_clients.remove(item)
        self.log.debug('Removed %s from connected_clients', str(item))
        return True


