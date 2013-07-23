#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = 'ibutils',
    version = '0.1',
    packages = find_packages(),
    entry_points = {
        'console_scripts': [
            'ibcondense = ibutils.condense:main',
            ],
        },

    include_package_data = True,
    package_data = {
        '': ['COPYING', 'README', 'Makefile'],
        },

    description = 'Image Book Utilities',
    author = 'Huang Ying',
    author_email = 'huang.ying.caritas@gmail.com',

    license = 'GPL',
    keywords = ('Image', 'Book', 'Scan'),
    platforms = 'Independent',
    zip_safe = False,
    )
