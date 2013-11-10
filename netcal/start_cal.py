#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 17:42:42
# @Last Modified by:   Giorgos Komninos
# @Last Modified time: 2013-11-10 17:58:18
import logging
import argparse

from netcal.client.node import Node

def parse_arguments():
    parser = argparse.ArgumentParser(description='''NetCal - Simple command
                                     line calendar tool''')
    parser.add_argument('-t', '--host', action="store", default='localhost',
                        help='''Please give the host/ip the calendar should
                         use''')
    parser.add_argument('-p', '--port', action='store', type=int,
                        default=12345, help='''Please give the port the
                        calendar should use''')
    parser.add_argument('-d', '--db', action='store', default='cal.db',
                        help='''Please give the filename to use for the
                        calendat's database''')
    parser.add_argument('-j', '--join', action='store', default=None,
                        help='''Insert the host:port to join''')
    return parser.parse_args()


def main():
    args = parse_arguments()
    logging.basicConfig(level=logging.DEBUG)
    cal_node = Node(host=args.host, port=args.port, db=args.db,
                    join=args.join)


if __name__ == '__main__':
    main()

