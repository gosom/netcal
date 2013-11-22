#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-22 18:50:33
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-22 19:01:49
"""use for posting xmlrpc request to the xmlrpc server.
Usage:
cat xml_rpc_request.xml|python manual_xmlrpc.py http://ip:port
"""
import sys
import requests


data = sys.stdin.read()
url = sys.argv[1]
try:
    r = requests.post(url, data=data)
except Exception as e:
    print >> sys.stderr, str(e)

print r.text
