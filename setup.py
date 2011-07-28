#!/usr/bin/env python

from distutils.core import setup

setup(name='Plainsight',
      version='1.0',
      description='A textual steganography tool.',
      author='Robert Winslow',
      author_email='robert.winslow@gmail.com',
      url='http://github.com/rw/plainsight',
      packages=['argparse', 'bitstring', 'progressbar'],
     )

