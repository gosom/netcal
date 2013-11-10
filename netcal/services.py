#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: Giorgos Komninos
# @Date:   2013-11-10 12:27:46
# @Last Modified by:   Giorgos Komninos
# @Last Modified time: 2013-11-10 13:36:42
import os

class NetCalService(object):
    """Here are all the functions we want to
    expose via xml-rpc"""

    def list(self, dir_name):
        """This is a demo funtion for testing purposes.
        It returns a list of the files in dir_name"""
        return os.listdir(dir_name)


