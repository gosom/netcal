#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 12:27:46
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-10 12:30:00
import os

class NetCalService(object):

    def list(self, dir_name):
        return os.listdir(dir_name)


