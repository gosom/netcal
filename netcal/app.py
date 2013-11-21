#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-17 13:43:30
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 09:01:41
import time
import logging
import sys

from cmd2 import Cmd, make_option, options
from prettytable import PrettyTable

from netcal.client.node import Node

def check_init(func):
    def wrapper(*args, **kwargs):
        if args[0].node:
            return func(*args, **kwargs)
        sys.stderr.write('Please call init first!\n')
        return False
    return wrapper

def check_connected(func):
    def wrapper(*args, **kwargs):
        if args[0].connected:
            return func(*args, **kwargs)
        sys.stderr.write('Please connect to the network first!\n')
        return False
    return wrapper

class NetCalCli(Cmd):
    """Simple command processor example."""

    def preloop(self):
        self.prompt = "=>> "
        self.intro  = "Welcome to netcal!"
        self.node = None
        self.connected = False

    @options([make_option('-b', '--bind', action="store", help="bind address"),
              make_option('-d', '--db', action="store", help="db file"),
              make_option('-c', '--connect', help="connect address")
             ])
    def do_init(self, command, opts):
        if not opts.bind:
            sys.stderr.write('Please provide a bind address\n')
            return False
        if not opts.db:
            sys.stderr.write('Please provide your local database file\n')
            return False
        # TODO validation of bind_address
        # here we start the actual program
        self.node = Node(my_address=opts.bind, db=opts.db)
        if opts.connect:
            self.__connect(opts.connect)

    @options([make_option('-c', '--connect', help='Connect to host')])
    def do_connect(self, command, opts):
        if not opts.connect:
            sys.stderr.write('please provide a host to connect\n')
            return False
        self.__connect(opts.connect)

    @check_init
    @options([make_option('-c', '--connect', help='Host to synchronize from')])
    def do_sync(self, command, opts):
        if not opts.connect:
            sys.stderr('please specify -c option')
            return False
        self.node.sync(opts.connect)

    @check_init
    @options([make_option('-t', '--datetime', help='Datetime of appointment'),
             make_option('-d', '--duration', help='''Duration of the appointment.
                         DEFAULT 1'''),
             make_option('-e', '--header', help='Header of the appointment',
                         type="string"),
             make_option('-c', '--comment', help='''Comment of the appointment.
                         Default empty''')
             ], 'hello')
    def do_add(self, command, opts):
        if not opts.datetime:
            sys.stderr.write('please specify the datetime of the appointment [-t option]\n')
            return False
        if not opts.header:
            sys.stderr.write('Please give a header for the appointment [-e option]\n')
            return False
        if not opts.duration:
            opts.duration = 1
        if not opts.comment:
            opts.comment = ''

        if self.node.add(date_time=opts.datetime, duration=opts.duration,
                         header=opts.header, comment=opts.comment) is False:
            sys.stderr.write('there was an error adding the appointment\n')
        else:
            sys.stdout.write('appointment was added\n')

    @check_init
    @options([make_option('-a', '--all', action='store_true',
             help='Enable to list all appointments. DEFAULT TRUE'),
             ])
    def do_list(self, command, opts):
        if opts.all:
            self.__print_list(self.node.list())
        else:
            sys.stderr.write('Not implemented yet\n')

    @check_init
    @options([make_option('-i', '--id', action='store',
             help='id to delete'),
             ])
    def do_view(self, command, opts):
        if not self.node:
            sys.stderr.write('Please call init first\n')
            return False
        if not opts.id:
            sys.stderr.write('Please give the id you wish to view\n')
            return False
        item = self.node.view(opts.id)
        if not item:
            sys.stderr.write('Does appointment with id %s exists?', opts.id)
        else:
            sys.stdout.write('uid: %s\n' % item['uid'])
            sys.stdout.write('datetime: %s\t' % item['datetime'])
            sys.stdout.write('duration: %s\n' % item['duration'])
            sys.stdout.write('header: %s\n' % item['header'])
            sys.stdout.write('comment: %s\n' % item['comment'])

    @check_init
    #@check_connected
    @options([make_option('-i', '--id', action='store',
             help='id to delete'),
             ])
    def do_delete(self, command, opts):
        if not self.node:
            sys.stderr.write('Please call init first\n')
            return False
        if not opts.id:
            sys.stderr.write('Please give the id you wish to delete\n')
            return False
        ret_value = self.node.delete(opts.id)
        if ret_value is None:
            sys.stderr.write('Error happened while deletion\n')
        elif ret_value < 1:
            sys.stderr.write('nothing was deleted. Does the uid exists?\n')
        else:
            sys.stdout.write('entry was deleted\n')

    @check_init
    @options([make_option('-i', '--id', help='the uid you wish to edit'),
             make_option('-t', '--datetime', help='Datetime of appointment'),
             make_option('-d', '--duration', help='Duration of the appointment'),
             make_option('-e', '--header', help='Header of the appointment',
                         type="string"),
             make_option('-c', '--comment', help='Comment of the appointment')
             ])
    def do_edit(self, command, opts):
        if not self.node:
            sys.stderr.write('Please first run init\n')
            return False
        if not opts.id:
            sys.stderr.write('Please give the id you wish to edit\n')
            return False

        things_to_edit = {'datetime': opts.datetime,
                          'duration': opts.duration,
                          'header': opts.header,
                          'comment': opts.comment}
        for t in things_to_edit.keys():
            if things_to_edit[t] is None:
                del things_to_edit[t]
        if not things_to_edit:
            sys.stderr.write('please edit at least one value\n')
        else:
            if self.node.edit(opts.id, things_to_edit):
                sys.stdout.write('Successfully edited %s\n' % opts.id)
            else:
                sys.stdout.write('Could not edit appointment\n')

    # helpers
    def __print_list(self, app_list):
        x = PrettyTable(['uid', 'datetime', 'duration', 'header', 'comment',
                        'last_modified'])
        for a in app_list:
            x.add_row([a['uid'],a['datetime'], a['duration'], a['header'],
                      a['comment'], a['last_modified']])
        sys.stdout.write(str(x))
        sys.stdout.write('\n')

    def __connect(self, address):
        if not self.node:
            sys.stderr.write("please first run init command\n")
            return False
        if not self.node.connect(address):
            sys.stderr.write('Could not connect to %s\n' % address)
            return False
        sys.stdout.write('connected to %s\n' % address)
        return True

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    NetCalCli().cmdloop()

