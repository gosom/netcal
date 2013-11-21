#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: giorgos
# @Date:   2013-11-21 10:03:35
# @Last Modified by:   giorgos
# @Last Modified time: 2013-11-21 10:41:48

#from distutils.core import setup
from setuptools import setup

setup(name='netcal',
      version='0.8',
      description='netcal application for hpn course',
      author='Giorgos Komninos',
      author_email='admin@gkomninos.com',
      packages=['netcal', 'netcal.client', 'netcal.dbo', 'netcal.srv',
      'netcal.utils', ],
      py_modules=['cmd2', 'pyparsing', 'prettytable'], # should not be here but...
     )
