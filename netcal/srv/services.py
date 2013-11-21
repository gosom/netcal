#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 12:27:46
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 07:53:44
import logging
import os
import datetime

import utils
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

    def add(self, date_time, duration, header, comment, uid, last_modified):
        '''adds an appointment to the database and propagates
        the appointment to the connected_clients'''
        try:
            item = self.db.insert(dt=date_time, dur=duration, he=header,
                                  com=comment, uid=uid, last_modified=last_modified)
        except Exception:
            self.log.exception('cannot insert appointment: %s %s %s %s',
                           date_time, duration, header, comment)
            return False
        else:
            self.log.debug('appointment %s %s was added', item['datetime'],
                           item['header'])
            return item

    def edit(self, uid, fields_to_edit):
        try:
            item = self.db.update(uid, fields_to_edit)
        except:
            self.log.exception('Exception while editing')
            return False
        else:
            return item

    def delete(self, uid):
        try:
            self.db.delete(uid)
        except:
            self.log.exception('cannot delete uid')
            return False
        else:
            return True
