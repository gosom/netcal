#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-17 13:43:30
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 11:07:55
import time
import logging
import sys

try:
    from cmd2 import Cmd, make_option, options
except ImportError:
    sys.stderr.write('''requires cmd2 module. Please install it using pip
                     [ pip install cmd2 ] and apply my patch (cmd2.patch) to fix
                     a critical bug\n''' )
    sys.exit(1)
try:
    from prettytable import PrettyTable
except ImportError:
    sys.stderr.write('''requires prettytable [ pip install prettytable ]\n''')
    sys.exit(1)

from netcal.client.node import Node

def check_init(func):
    """use it to decorate methods in class NetCalCli.
    If the cal node is not initialized returns False"""
    def wrapper(*args, **kwargs):
        if args[0].node:
            return func(*args, **kwargs)
        sys.stdout.write('Please call init first!\n')
        return False
    return wrapper

def check_connected(func):
    """decorator function to check if the calendar node is connected."""
    def wrapper(*args, **kwargs):
        if args[0].connected:
            return func(*args, **kwargs)
        sys.stdout.write('Please connect to the network first!\n')
        return False
    return wrapper

class NetCalCli(Cmd):
    """Command line interface for netcal"""

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
            self.__print_error('Please provide a bind address\n')
            return False
        if not opts.db:
            self.__print_error('Please provide your local database file\n')
            return False
        # TODO validation of bind_address
        # here we start the actual program
        self.node = Node(my_address=opts.bind, db=opts.db)
        if opts.connect:
            self.__connect(opts.connect)

    @options([make_option('-c', '--connect', help='Connect to host')])
    def do_connect(self, command, opts):
        if not opts.connect:
            self.__print_error('please provide a host to connect\n')
            return False
        self.__connect(opts.connect)

    @check_init
    @options([make_option('-c', '--connect', help='Host to synchronize from')])
    def do_sync(self, command, opts):
        if not opts.connect:
            self.__print_error('please specify -c option')
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
            self.__print_error('please specify the datetime of the appointment [-t option]\n')
            return False
        if not opts.header:
            self.__print_error('Please give a header for the appointment [-e option]\n')
            return False
        if not opts.duration:
            opts.duration = 1
        if not opts.comment:
            opts.comment = ''

        if self.node.add(date_time=opts.datetime, duration=opts.duration,
                         header=opts.header, comment=opts.comment) is False:
            sys.stdout.write('there was an error adding the appointment\n')
        else:
            sys.stdout.write('appointment was added\n')

    @check_init
    def do_list(self, command):
        self.__print_list(self.node.list())

    @check_init
    @options([make_option('-i', '--id', action='store',
             help='id to delete'),
             ])
    def do_view(self, command, opts):
        if not self.node:
            self.__print_error('Please call init first\n')
            return False
        if not opts.id:
            self.__print_error('Please give the id you wish to view\n')
            return False
        item = self.node.view(opts.id)
        if not item:
            self.__print_error('Does appointment with id %s exists?', opts.id)
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
            sys.stdout.write('Please call init first\n')
            return False
        if not opts.id:
            sys.stdout.write('Please give the id you wish to delete\n')
            return False
        ret_value = self.node.delete(opts.id)
        if ret_value is None:
            sys.stdout.write('Error happened while deletion\n')
        elif ret_value < 1:
            sys.stdout.write('nothing was deleted. Does the uid exists?\n')
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
            self.__print_error('Please first run init\n')
            return False
        if not opts.id:
            self.__print_error('Please give the id you wish to edit\n')
            return False

        things_to_edit = {'datetime': opts.datetime,
                          'duration': opts.duration,
                          'header': opts.header,
                          'comment': opts.comment}
        for t in things_to_edit.keys():
            if things_to_edit[t] is None:
                del things_to_edit[t]
        if not things_to_edit:
            self.__print_error('please edit at least one value\n')
        else:
            if self.node.edit(opts.id, things_to_edit):
                sys.stdout.write('Successfully edited %s\n' % opts.id)
            else:
                self.__print_error('Could not edit appointment\n')

    @check_init
    #@check_connected
    @options([make_option('-v', '--verbose', action='store_true',
             help='use for more verbose output'),
             ])
    def do_debug(self, command, opts):
        if opts.verbose:
            self.node.log.setLevel(logging.DEBUG)
        else:
            self.node.log.setLevel(logging.INFO)


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
            sys.stdout.write("please first run init command\n")
            return False
        if not self.node.connect(address):
            sys.stdout.write('Could not connect to %s\n' % address)
            return False
        sys.stdout.write('connected to %s\n' % address)
        return True

    def do_EOF(self, line):
        return True

    def __print_error(self, msg):
        sys.stdout.write(self.colorize(msg, 'red'))

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    NetCalCli().cmdloop()

