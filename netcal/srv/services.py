#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging
import os
import datetime

import netcal.utils
from netcal.dbo.db import DB


class NetCalService(object):
    """Here are all the functions we want to
    expose via xml-rpc"""

    def __init__(self, connected_clients, db_name, token_ring):
        """connectected clients is a dict of
        the nodes connected to the network"""
        self.log = logging.getLogger(self.__class__.__name__)
        self.connected_clients = connected_clients
        self.db = DB(db_name)
        self.token_ring = token_ring

    def get_clients(self,address):
        """Returns a list of all connected clients.
        In the xml-rpc this should be an array"""
        self.log.debug('returning %s', str(self.connected_clients.keys()))
        return self.connected_clients.keys()

    def signin(self, address):
        if address not in self.connected_clients:
            self.connected_clients[address] = None
            self.log.debug('adding %s to connected_clients', address)
            return int(0)
        return int(1)

    def sign_off(self, address):
        if address in self.connected_clients:
            del self.connected_clients[address]
            self.log.debug('Removed %s from connected_clients', address)
            return int(0)
        return int(1)

        # pull
    def getTableData(self, address):
        """pull function returns a snapshot of the changes
        of the database after timestamp"""
        if address not in self.connected_clients:
            self.log.error('%s is not on connected_clients')
            raise
        else:
            updated_rows = self.db.get_updated()
            if updated_rows:
                self.log.debug('Returning %d updated_rows', len(updated_rows))
            else:
                self.log.debug('there are no rows modified')

            ret = []
            for r in updated_rows:
                ret.append(r['uid'])
                ret.append(r['date'])
                ret.append(r['time'])
                ret.append(r['duration'])
                ret.append(r['header'])
                ret.append(r['comment'])
            return ret

    def addRowClient(self, date, time, duration, header, comment):
        '''adds an appointment to the database and propagates
        the appointment to the connected_clients'''
        try:
            item = self.db.insert(dt=date, tm=time, dur=duration, he=header,
                                  com=comment)
        except Exception:
            self.log.exception('cannot insert appointment: %s %s %s %s %s',
                           date,time, duration, header, comment)
            return int(1)
        else:
            return int(0)

    def editRowClient(self, uid, date, time, duration, header, comment):
        try:
            item = self.db.edit(uid, date, time, duration, header, comment)
        except:
            self.log.exception('Exception while editing')
            return int(1)
        else:
            return int(0)

    def delete_all(self):
        try:
            self.db.delete_all()
        except:
            self.log.exception('cannot delete')
            return False
        else:
            return True

    def delRowClient(self, uid):
        try:
            ret_value = self.db.delete(uid)
            if ret_value != 1:
                raise Exception('Not exists')
        except:
            self.log.exception('cannot delete uid')
            return int(1)
        else:
            return int(0)

    def tokenReceived(self, address):
        #self.log.debug('Received token from %s', address)
        self.token_ring.token = True


