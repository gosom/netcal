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

    def __init__(self, node, connected_clients, db_name):
        """connectected clients is a dict of
        the nodes connected to the network"""
        self.log = logging.getLogger(self.__class__.__name__)
        self.connected_clients = connected_clients
        self.db = DB(db_name)
        self.node = node

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

    def sign_in_approved(self, src_address):
        self.log.debug('Calling signInApproved method')
        self.node.signin(src_address)

    def rclient_signin(self, address):
        self.log.debug('rpc call request_client_signin')
        self.node.token_ring.signin_q.put(address)
        return int(0)

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
            self.log.error('%s is not on connected_clients', address)
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
        self.node.token_ring.token = True
        return int(0)

    def function_to_perform(self, function_id, ap_id, ap_date, ap_time, ap_duration,
                            ap_header,ap_comment):
        try:
            assert function_id in (1, 2, 3)
        except AssertionError:
            self.log.error('Function_id should be in (1,2,3)')
            return int(1)
        if function_id == 1:
            self.addRowClient(date=ap_date, time=ap_time, duration=ap_duration,
                              header=ap_header, comment=ap_comment)
        elif function_id == 2:
            self.delRowClient(uid=ap_id)
        elif function_id == 3:
            self.editRowClient(uid=ap_id, date=ap_date, time=ap_time,
                               duration=ap_duration, header=ap_header,
                               comment=ap_comment)
        return 0

    def cs_request_received(self, resource_id, remote_host, remote_clock):
        self.node.cs_request_received(resource_id, remote_host, remote_clock)
        return 0

    def reply_received(self, address):
        self.log.debug('Received reply from %s', address)
        self.node.reply_received(address)
        return 0


