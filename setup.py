#!/usr/bin/env python

from setuptools import setup

setup(name='Plainsight',
      version='1.0a',
      description='A textual steganography tool to defeat censorship.',
      author='Robert Winslow',
      author_email='robert.winslow@gmail.com',
      url='http://github.com/rw/plainsight',
      classifiers=['Development Status :: 4 - Beta',
                   'Intended Audience :: Developers',
                   'Intended Audience :: End Users/Desktop',
                   'Natural Language :: English',
                   'Programming Language :: Python',
                   'Topic :: Security :: Cryptography'
                   'Topic :: Text Processing :: Filters',
                   'Topic :: Text Processing :: Linguistic',
                  ],
      requires=['argparse', 'bitstring', 'progressbar'],
     )

