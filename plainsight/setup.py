#!/usr/bin/env python

from setuptools import setup
from sys import version


setup(name='Plainsight',
      version='1.0',
      description='A textual steganography tool.',
      author='Robert Winslow',
      author_email='robert.winslow@gmail.com',
      url='http://github.com/rw/plainsight',
      requires=['argparse', 'bitstring', 'progressbar'],
     )

