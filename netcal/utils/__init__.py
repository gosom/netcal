#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""this module contains some helper functions"""
import socket
import string
import random

def check_connection(host, port):
    """returns True if the host is readchable
    and port port is open"""
    assert isinstance(host, basestring)
    assert isinstance(port, int)
    ok = False
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(0.2)
    try:
        sock.connect((host, port))
    except socket.error:
        pass
    else:
        ok = True
    finally:
        sock.close()
    return ok

def generate_random_uid(length=8):
    """generates random string of the specified length"""
    charset = string.ascii_letters + string.digits
    return ''.join(random.choice(charset) for _ in xrange(length))
