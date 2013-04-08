#!/usr/bin/env python

import kstat

from distutils.core import setup

setup(name='kstat',
      version=kstat.__version__,
      author=kstat.__author__,
      packages=['kstat'],
)
