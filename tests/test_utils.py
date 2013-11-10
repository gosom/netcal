#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-10 16:58:25
# @Last Modified by:   Giorgos Komninos
# @Last Modified time: 2013-11-10 17:06:59
import netcal.utils as utils

def test_check_connection(host, port):
    if utils.check_connection(host, port):
        print 'connected'
    else:
        print 'connection failed'

if __name__ == '__main__':

    test_check_connection('localhost', 12345)


