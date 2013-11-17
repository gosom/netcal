#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 12:27:46
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-17 11:57:09
import logging
import os
from netcal.dbo.db import DB

class NetCalService(object):
    """Here are all the functions we want to
    expose via xml-rpc"""

    def __init__(self, connected_clients, db_name):
        """connectected clients is a dict of
        the nodes connected to the network"""
        self.log = logging.getLogger(self.__class__.__name__)
        self.connected_clients = connected_clients
        self.db = DB(db_name)

    def get_clients(self,):
        """Returns a list of all connected clients.
        In the xml-rpc this should be an array"""
        self.log.debug('returning %s', str(self.connected_clients.keys()))
        return self.connected_clients.keys()

    def signin(self, address):
        if address not in self.connected_clients:
            self.connected_clients[address] = None
            self.log.debug('adding %s to connected_clients', address)
            return True
        return False

    def sign_off(self, address):
        if address in self.connected_clients:
            del self.connected_clients[address]
            self.log.debug('Removed %s from connected_clients', address)
            return True
        return False

    def pull(self, address, timestamp):
        """pull function returns a snapshot of the changes
        of the database after timestamp"""
        if address not in self.connected_clients:
            self.log.error('%s is not on connected_clients')
            raise
        else:
            updated_rows = self.db.get_updated(timestamp)
            if updated_rows:
                self.log.debug('Returning %d updated_rows', len(updated_rows))
            else:
                self.log.debug('there are no rows modified')
            return updated_rows if updated_rows else []




