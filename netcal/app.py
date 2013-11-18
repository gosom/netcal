#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-17 13:43:30
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-18 19:35:22
import time
import logging
import sys

from cmd2 import Cmd, make_option, options
from prettytable import PrettyTable

from netcal.client.node import Node

class NetCalCli(Cmd):
    """Simple command processor example."""

    def preloop(self):
        self.prompt = "=>> "
        self.intro  = "Welcome to netcal!"

    @options([make_option('-b', '--bind', action="store", help="bind address"),
              make_option('-d', '--db', action="store", help="db file"),
              make_option('-c', '--connect', help="connect address")
             ], arg_desc = '(text to say)')
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

    @options([make_option('-t', '--datetime', help='Datetime of appointment'),
             make_option('-d', '--duration', help='''Duration of the appointment.
                         DEFAULT 1'''),
             make_option('-e', '--header', help='Header of the appointment'),
             make_option('-c', '--comment', help='''Comment of the appointment.
                         Default empty''')
             ])
    def do_add(self, command, opts):
        if not self.node:
            sys.stderr.write('please first initialize calendar with init command\n')
            return False
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

        if not self.node.add(date_time=opts.datetime, duration=opts.duration,
                         header=opts.header, comment=opts.comment):
            sys.stderr.write('there was an error adding the appointment\n')
        else:
            sys.stdout.write('appointment was added\n')

    @options([make_option('-a', '--all', action='store_true',
             help='Enable to list all appointments. DEFAULT TRUE'),
             ])
    def do_list(self, command, opts):
        if opts.all:
            self.__print_list(self.node.list())
        else:
            sys.stderr.write('Not implemented yet\n')

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

    def do_greet(self, line):
        print "hello"

    def do_EOF(self, line):
        return True

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    NetCalCli().cmdloop()

