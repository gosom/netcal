#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-21 21:49:06
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 22:09:42
import xmlrpclib


def debug_get_clients():
    call_string = xmlrpclib.dumps((), 'get_clients')
    with open('get_clients.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))

def debug_signin():
    call_string = xmlrpclib.dumps(('192.168.1.1:8080',), 'signin')
    with open('signin.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))

def debug_sign_off():
    call_string = xmlrpclib.dumps(('192.168.1.1:8080',), 'sign_off')
    with open('sign_off.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))

def debug_pull():
    import datetime
    address = '192.168.1.1:8080'
    ts = datetime.datetime.now().isoformat()
    class_string = xmlrpclib.dumps((address, ts), 'pull')
    with open('pull.xml', 'wb') as f:
        f.write(class_string.encode('utf8'))

def debug_add():
    date_time = '2013-01-01'
    duration = "0.5"
    header = "appointment header"
    comment = "comment here"
    uid = ''
    last_modified = ''
    call_string = xmlrpclib.dumps((date_time, duration, header, comment,
                                   uid, last_modified), 'add')
    with open('add.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))

def debug_edit():
    fields_to_edit = {'datetime': '2013-01-01',
                      'comment': "you can add any field here"}
    uid = '13rfdgt5'
    call_string = xmlrpclib.dumps((uid, fields_to_edit), 'edit')
    with open('edit.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))

def debug_delete():
    uid = '13rfdgt5'
    call_string = xmlrpclib.dumps((uid,), 'delete')
    with open('delete.xml', 'wb') as f:
        f.write(call_string.encode('utf8'))




if __name__ == '__main__':

    debug_get_clients()

    debug_signin()

    debug_sign_off()

    debug_pull()

    debug_add()

    debug_delete()

    debug_edit()





