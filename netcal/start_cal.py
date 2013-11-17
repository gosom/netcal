#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 17:42:42
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-16 16:40:33
import logging
import argparse
import time

from netcal.client.node import Node

def parse_arguments():
    parser = argparse.ArgumentParser(description='''NetCal - Simple command
                                     line calendar tool''')
    parser.add_argument('-b', '--bind', action="store", default='localhost:12345',
                        help='''Please give the ip:port to use''')
    parser.add_argument('-d', '--db', action='store', default='cal.db',
                        help='''Please give the filename to use for the
                        calendat's database''')
    parser.add_argument('-c', '--connect', action='store', default=None,
                        help='''Insert the host:port to join''')
    return parser.parse_args()


def main():
    args = parse_arguments()
    logging.basicConfig(level=logging.DEBUG)

    cal_node = Node(my_address=args.bind, db=args.db)
    if args.connect:
        cal_node.connect(args.connect)


if __name__ == '__main__':
    main()
    while True:
        try:
            time.sleep(0.2)
        except KeyboardInterrupt:
            break

