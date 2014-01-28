#!/usr/bin/env python
# -*- coding: utf-8 -*-
import logging


class LamportClock(object):

    def __init__(self, clock, own_id):
        self.log = logging.getLogger(self.__class__.__name__)
        self.clock = clock
        self.own_id = own_id

    def __cmp__(self, other):
        if self.clock < other.clock:
            return -1
        elif self.clock > other.clock:
            return 1
        # compare ips
        myadd, port = self.own_id.split(':')
        otheradd, otherport = other.own_id.split(':')

        myadd_number = self.from_string(myadd)
        otheradd_number = self.from_string(otheradd)
        #o1, o2, o3, o4 = myadd.split('.')
        #myadd_number = o1 * 256*256*256 + o2 *256*256 + o3 * 256 + o4

        #o1, o2, o3, o4 = otheradd.split('.')
        #otheradd_number = o1 * 256*256*256 + o2 *256*256 + o3 * 256 + o4

        if myadd_number < otheradd_number:
            return -1
        elif myadd_number > otheradd_number:
            return 1

        myport, otherport = int(port), int(otherport)
        if myport < otherport:
            return -1
        elif myport > otherport:
            return 1

        return 0

    def from_string(self, s):
        return reduce(lambda a, b: a<< 8 | b, map(int, s.split(".")))


if __name__ == '__main__':
    lc = LamportClock(0, "127.0.0.0:8000")
    lc2 = LamportClock(0, "127.0.0.0:8000")

    print lc.from_string("127.0.0.1")
    print lc.from_string("127.0.0.0")

    print lc < lc2

